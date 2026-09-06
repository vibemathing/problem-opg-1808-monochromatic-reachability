// Candidate-side bounded search. No trusted-verifier or mathematical-admission claim.
// g++ -O3 -std=c++17 root-interval-search-r03.cpp -o interval-search
// N PALETTE FORBID_RAINBOW MODE SECONDS NODE_CAP CYCLE_WORD
// MODE 0: global requirements; 1: cyclic-interval requirements; 2: also boundary cuts.
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
constexpr int M=16,K=4;
using Bits=uint32_t;
struct State { uint8_t a[M][M]{}; Bits lo[K][M]{}; };
struct Arc {int u,v,c;};
struct Domain {int u,v; vector<Arc> choices;};
int n,k,nr,mode; double seconds_limit; uint64_t node_limit;
uint64_t nodes=0,trials=0,triangle_reject=0,lower_reject=0,empty_reject=0;
uint64_t support_reject=0,forced_reach=0,forced_arcs=0,boundary_arcs=0,rounds=0;
bool stopped=false,found=false;State model;
vector<pair<int,int>> pairs;
Bits intervals[M][M]{},full;
chrono::steady_clock::time_point started;
Bits bit(int x){return Bits(1)<<x;}
int pred(int x){return (x+n-1)%n;}
double elapsed(){return chrono::duration<double>(chrono::steady_clock::now()-started).count();}
// lo is a transitive LOWER bound, not necessarily a physical path graph.
bool possible_reach(const State&s,int u,int v,int c){
 Bits succ=s.lo[c][v];
 for(int x=0;x<n;++x)if((s.lo[c][x]&bit(u))&&(succ&bit(pred(x))))return false;
 return true;
}
void insert_reach(State&s,int u,int v,int c){
 Bits succ=s.lo[c][v];
 // Updating row x cannot newly put u in another row, since rows change independently.
 for(int x=0;x<n;++x)if(s.lo[c][x]&bit(u))s.lo[c][x]|=succ;
}
bool possible_arc(const State&s,Arc q){
 ++trials;
 if(nr)for(int w=0;w<n;++w)if(s.a[q.v][w]&&s.a[w][q.u]){
  int a=s.a[q.v][w]-1,b=s.a[w][q.u]-1;
  if(q.c!=a&&q.c!=b&&a!=b){++triangle_reject;return false;}
 }
 if(!possible_reach(s,q.u,q.v,q.c)){++lower_reject;return false;}
 return true;
}
bool insert_arc(State&s,Arc q){
 if(s.a[q.u][q.v])return s.a[q.u][q.v]==q.c+1;
 if(s.a[q.v][q.u]||!possible_arc(s,q))return false;
 s.a[q.u][q.v]=q.c+1;insert_reach(s,q.u,q.v,q.c);return true;
}
Bits reachable(const Bits adj[M],int start,Bits allowed){
 Bits seen=bit(start),todo=seen;
 while(todo){int u=__builtin_ctz(todo);todo&=todo-1;
  Bits added=adj[u]&allowed&~seen;seen|=added;todo|=added;
 }
 return seen;
}
void close(Bits adj[K][M]){
 for(int c=0;c<k;++c)for(int w=0;w<n;++w)for(int u=0;u<n;++u)
  if(adj[c][u]&bit(w))adj[c][u]|=adj[c][w];
}
bool propagate(State&s,vector<Domain>&ds){
 for(;;){
  ++rounds; ds.clear();Bits adj[K][M]{},rev[K][M]{};
  bool restart=false;
  for(auto [u,v]:pairs){
   if(s.a[u][v]){int c=s.a[u][v]-1;adj[c][u]|=bit(v);rev[c][v]|=bit(u);continue;}
   if(s.a[v][u]){int c=s.a[v][u]-1;adj[c][v]|=bit(u);rev[c][u]|=bit(v);continue;}
   Domain d{u,v,{}};
   for(int dir=0;dir<2;++dir)for(int c=0;c<k;++c){
    Arc q{dir?v:u,dir?u:v,c};
    if(possible_arc(s,q)){d.choices.push_back(q);adj[c][q.u]|=bit(q.v);rev[c][q.v]|=bit(q.u);}
   }
   if(d.choices.empty()){++empty_reject;return false;}
   if(d.choices.size()==1){
    if(!insert_arc(s,d.choices[0]))throw logic_error("fresh singleton invalid");
    ++forced_arcs;restart=true;break;
   }
   ds.push_back(std::move(d));
  }
  if(restart)continue;
  Bits hi[K][M]{};
  for(int c=0;c<k;++c)for(int u=0;u<n;++u)hi[c][u]=adj[c][u]|bit(u);
  close(hi);
  for(int c=0;c<k;++c)for(int u=0;u<n;++u)if(s.lo[c][u]&~hi[c][u]){
   ++support_reject;return false;
  }
  bool changed=false;
  for(int u=0;u<n&&!restart;++u)for(int v=0;v<n&&!restart;++v){
   if(v==u||v==pred(u))continue;
   Bits allowed=mode?intervals[u][v]:full;
   int count=0,only=-1;
   for(int c=0;c<k;++c){
    if(!(hi[c][u]&bit(v))||!possible_reach(s,u,v,c))continue;
    if(mode&&!(reachable(adj[c],u,allowed)&bit(v)))continue;
    ++count;only=c;
   }
   if(count==0){++support_reject;return false;}
   if(count!=1)continue;
   if(!(s.lo[only][u]&bit(v))){insert_reach(s,u,v,only);++forced_reach;changed=true;}
   if(mode<2)continue;
   // A simple physical path cannot revisit its first vertex or its last vertex.
   Bits first=adj[only][u]&allowed&reachable(rev[only],v,allowed&~bit(u));
   Bits last=rev[only][v]&allowed&reachable(adj[only],u,allowed&~bit(v));
   if(!first||!last){++support_reject;return false;}
   Arc force{-1,-1,only};
   if(__builtin_popcount(first)==1){int w=__builtin_ctz(first);if(!s.a[u][w])force={u,w,only};}
   if(force.u<0&&__builtin_popcount(last)==1){int w=__builtin_ctz(last);if(!s.a[w][v])force={w,v,only};}
   if(force.u>=0){
    if(!insert_arc(s,force)){++support_reject;return false;}
    ++boundary_arcs;restart=true;
   }
  }
  if(restart||changed)continue;
  return true;
 }
}
bool audit(const State&s){
 Bits adj[K][M]{};
 for(auto [u,v]:pairs){if(bool(s.a[u][v])==bool(s.a[v][u]))return false;
  if(s.a[u][v])adj[s.a[u][v]-1][u]|=bit(v);else adj[s.a[v][u]-1][v]|=bit(u);
 }
 for(int u=0;u<n;++u){if(!s.a[u][(u+1)%n])return false;
  Bits all=0;for(int c=0;c<k;++c){Bits r=reachable(adj[c],u,full);if(r&bit(pred(u)))return false;all|=r;}
  if(all!=(full^bit(pred(u))))return false;
  if(mode)for(int v=0;v<n;++v)if(v!=u&&v!=pred(u)){
   bool ok=false;for(int c=0;c<k;++c)if(reachable(adj[c],u,intervals[u][v])&bit(v))ok=true;
   if(!ok)return false;
  }
 }
 if(nr)for(int u=0;u<n;++u)for(int v=0;v<n;++v)for(int w=0;w<n;++w)
  if(s.a[u][v]&&s.a[v][w]&&s.a[w][u]&&s.a[u][v]!=s.a[v][w]&&s.a[v][w]!=s.a[w][u]&&s.a[w][u]!=s.a[u][v])return false;
 return true;
}
void dfs(State s){
 if(stopped||found)return;
 ++nodes;
 if(nodes>node_limit||(nodes%64==0&&elapsed()>seconds_limit)){stopped=true;return;}
 vector<Domain>ds;if(!propagate(s,ds))return;
 if(ds.empty()){if(!audit(s))throw logic_error("physical leaf audit failed");model=s;found=true;return;}
 auto best=min_element(ds.begin(),ds.end(),[](const Domain&a,const Domain&b){return a.choices.size()<b.choices.size();});
 for(Arc q:best->choices){State t=s;if(!insert_arc(t,q))throw logic_error("fixed-point domain invalid");dfs(t);if(stopped||found)return;}
}
int main(int argc,char**argv){try{
 if(argc!=8)throw invalid_argument("N PALETTE FORBID_RAINBOW MODE SECONDS NODE_CAP CYCLE_WORD");
 n=stoi(argv[1]);k=stoi(argv[2]);nr=stoi(argv[3]);mode=stoi(argv[4]);seconds_limit=stod(argv[5]);node_limit=stoull(argv[6]);string word=argv[7];
 if(n<3||n>M||k<1||k>K||(nr!=0&&nr!=1)||mode<0||mode>2||!(seconds_limit>0)||!node_limit||int(word.size())!=n)throw invalid_argument("invalid parameters");
 for(char c:word)if(c<'0'||c>='0'+k)throw invalid_argument("invalid colour");
 full=bit(n)-1;
 for(int u=0;u<n;++u){Bits mask=bit(u);for(int d=1;d<n;++d){int v=(u+d)%n;mask|=bit(v);intervals[u][v]=mask;}}
 for(int u=0;u<n;++u)for(int v=u+1;v<n;++v)pairs.push_back({u,v});
 State s;for(int c=0;c<k;++c)for(int u=0;u<n;++u)s.lo[c][u]=bit(u);
 started=chrono::steady_clock::now();bool ok=true;
 for(int u=0;u<n;++u)if(!insert_arc(s,{u,(u+1)%n,word[u]-'0'})){ok=false;break;}
 if(ok)dfs(s);
 cout<<"{\"n\":"<<n<<",\"palette\":"<<k<<",\"forbid_rainbow\":"<<nr<<",\"mode\":"<<mode<<",\"word\":\""<<word<<"\",\"status\":\""<<(stopped?"incomplete":found?"witness":"exhausted_no_witness")<<"\",\"nodes\":"<<nodes<<",\"trials\":"<<trials<<",\"triangle_reject\":"<<triangle_reject<<",\"lower_reject\":"<<lower_reject<<",\"empty_reject\":"<<empty_reject<<",\"support_reject\":"<<support_reject<<",\"forced_reach\":"<<forced_reach<<",\"forced_arcs\":"<<forced_arcs<<",\"boundary_arcs\":"<<boundary_arcs<<",\"rounds\":"<<rounds<<",\"seconds\":"<<elapsed()<<",\"arcs\":[";
 if(found){bool first=true;for(int u=0;u<n;++u)for(int v=0;v<n;++v)if(model.a[u][v]){if(!first)cout<<",";first=false;cout<<"["<<u<<","<<v<<","<<model.a[u][v]-1<<"]";}}
 cout<<"]}\n";return stopped?2:0;
 }catch(const exception&e){cerr<<e.what()<<"\n";return 1;}}
