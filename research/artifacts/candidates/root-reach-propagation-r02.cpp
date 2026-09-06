// Candidate-generator search; not a trusted mathematical verifier.
// Exact finite domain: a spanning forbidden-predecessor cycle, plus all other
// ordered pairs reachable in at least one colour (minimal-counterexample domain).
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
constexpr int M=12, K=4;
using Bits=uint16_t;
struct State { int a[M][M]{}; Bits lo[K][M]{}; int assigned=0; };
struct Choice {int u,v,c;};
struct Domain {int u,v; vector<Choice> values;};
int n,k,nr,mode; double seconds_limit; uint64_t node_limit;
uint64_t nodes=0,trials=0,triangle_reject=0,lower_reject=0,empty_domain=0;
uint64_t upper_reject=0,forced_reach=0,leaves=0,rounds=0;
bool stopped=false,found=false; State model;
vector<pair<int,int>> pairs;
chrono::steady_clock::time_point started;
int pred(int v){return (v+n-1)%n;}
double elapsed(){return chrono::duration<double>(chrono::steady_clock::now()-started).count();}
// Insert a necessary reachability, NOT an actual arc. Closure may contain
// unmaterialised path obligations; the final model is checked from physical arcs.
bool add_reach(const State&s,int u,int v,int c,State&t){
 t=s; Bits succ=s.lo[c][v];
 for(int x=0;x<n;++x)if(s.lo[c][x]&(1u<<u)) t.lo[c][x]|=succ;
 for(int x=0;x<n;++x)if(t.lo[c][x]&(1u<<pred(x)))return false;
 return true;
}
bool extend(const State&s,Choice q,State&t){
 ++trials;int u=q.u,v=q.v,c=q.c;
 if(nr)for(int w=0;w<n;++w)if(s.a[v][w]&&s.a[w][u]){
  int x=s.a[v][w]-1,y=s.a[w][u]-1;
  if(c!=x&&c!=y&&x!=y){++triangle_reject;return false;}
 }
 if(!add_reach(s,u,v,c,t)){++lower_reject;return false;}
 t.a[u][v]=c+1;++t.assigned;return true;
}
void close(Bits r[K][M]){
 for(int c=0;c<k;++c)for(int w=0;w<n;++w)for(int u=0;u<n;++u)
  if(r[c][u]&(1u<<w))r[c][u]|=r[c][w];
}
bool propagate(State&s,vector<Domain>&domains){
 // A successful round with a new fact strictly enlarges at least one of
 // k*n*n finite lower-closure bits. No loop can add the same fact twice.
 for(;;){
  ++rounds;domains.clear();Bits hi[K][M]{};
  for(int c=0;c<k;++c)for(int u=0;u<n;++u)hi[c][u]=1u<<u;
  for(auto [u,v]:pairs){
   if(s.a[u][v]){hi[s.a[u][v]-1][u]|=1u<<v;continue;}
   if(s.a[v][u]){hi[s.a[v][u]-1][v]|=1u<<u;continue;}
   Domain d{u,v,{}};
   for(int dir=0;dir<2;++dir){int x=dir?v:u,y=dir?u:v;
    if((y+1)%n==x)continue; // fixed cycle orientation
    for(int c=0;c<k;++c){State t;Choice q{x,y,c};
     if(extend(s,q,t)){d.values.push_back(q);hi[c][x]|=1u<<y;}
    }
   }
   if(d.values.empty()){++empty_domain;return false;}
   domains.push_back(std::move(d));
  }
  if(mode==0)return true;
  close(hi);
  // hi uses PHYSICAL arcs/domain choices only, never mandatory shortcuts.
  for(int c=0;c<k;++c)for(int u=0;u<n;++u)
   if(s.lo[c][u]&~hi[c][u]){++upper_reject;return false;}
  bool changed=false;
  for(int u=0;u<n;++u)for(int v=0;v<n;++v){
   if(u==v||v==pred(u))continue;
   bool known=false;for(int c=0;c<k;++c)if(s.lo[c][u]&(1u<<v))known=true;
   if(known)continue;
   int count=0,only=-1;
   for(int c=0;c<k;++c)if(hi[c][u]&(1u<<v)){
    State t;if(add_reach(s,u,v,c,t)){++count;only=c;}
   }
   if(count==0){++upper_reject;return false;}
   if(mode==2&&count==1){State t;if(!add_reach(s,u,v,only,t))throw logic_error("reach changed");
    s=t;++forced_reach;changed=true;
   }
  }
  if(!changed)return true;
 }
}
bool final_audit(const State&s){
 Bits r[K][M]{};for(int c=0;c<k;++c)for(int u=0;u<n;++u)r[c][u]=1u<<u;
 for(auto[u,v]:pairs){if(bool(s.a[u][v])==bool(s.a[v][u]))return false;
  if(s.a[u][v])r[s.a[u][v]-1][u]|=1u<<v;
  else r[s.a[v][u]-1][v]|=1u<<u;
 }
 close(r);
 for(int u=0;u<n;++u){Bits all=0;for(int c=0;c<k;++c){
   if(r[c][u]&(1u<<pred(u)))return false;
   all|=r[c][u];}
  if(mode&&all!=(((1u<<n)-1)^(1u<<pred(u))))return false;
 }
 if(nr)for(int u=0;u<n;++u)for(int v=0;v<n;++v)for(int w=0;w<n;++w)
  if(s.a[u][v]&&s.a[v][w]&&s.a[w][u]&&s.a[u][v]!=s.a[v][w]&&s.a[v][w]!=s.a[w][u]&&s.a[w][u]!=s.a[u][v])return false;
 return true;
}
void dfs(State s){
 if(stopped||found)return;
 ++nodes;
 if(nodes>node_limit || (nodes%128==0&&elapsed()>seconds_limit)){stopped=true;return;}
 vector<Domain>ds;if(!propagate(s,ds))return;
 if(ds.empty()){
  ++leaves;if(!final_audit(s))throw logic_error("physical leaf audit failed");model=s;found=true;return;
 }
 const Domain*best=&ds[0];for(auto&d:ds)if(d.values.size()<best->values.size())best=&d;
 for(auto q:best->values){State t;if(!extend(s,q,t))throw logic_error("stale domain");dfs(t);if(stopped||found)return;}
}
int main(int argc,char**argv){try{
 if(argc!=8)throw invalid_argument("N PALETTE NO_RAINBOW MODE SECONDS NODE_CAP CYCLE_WORD");
 n=stoi(argv[1]);k=stoi(argv[2]);nr=stoi(argv[3]);mode=stoi(argv[4]);seconds_limit=stod(argv[5]);node_limit=stoull(argv[6]);string word=argv[7];
 if(n<3||n>M||k<1||k>K||(nr!=0&&nr!=1)||mode<0||mode>2||seconds_limit<=0||!node_limit||int(word.size())!=n)throw invalid_argument("invalid domain");
 for(char c:word)if(c<'0'||c>='0'+k)throw invalid_argument("invalid cycle colour");
 State s;for(int c=0;c<k;++c)for(int u=0;u<n;++u)s.lo[c][u]=1u<<u;
 for(int u=0;u<n;++u)for(int v=u+1;v<n;++v)pairs.push_back({u,v});
 started=chrono::steady_clock::now();bool ok=true;
 for(int u=0;u<n;++u){State t;if(!extend(s,{u,(u+1)%n,word[u]-'0'},t)){ok=false;break;}s=t;}
 if(ok)dfs(s);
 cout<<"{\"n\":"<<n<<",\"palette\":"<<k<<",\"no_rainbow\":"<<(nr?"true":"false")<<",\"mode\":"<<mode<<",\"cycle_word\":\""<<word<<"\",\"status\":\""<<(stopped?"incomplete":found?"witness":"exhausted_no_witness")<<"\",\"nodes\":"<<nodes<<",\"trials\":"<<trials<<",\"triangle_reject\":"<<triangle_reject<<",\"lower_reject\":"<<lower_reject<<",\"empty_domain\":"<<empty_domain<<",\"upper_reject\":"<<upper_reject<<",\"forced_reach\":"<<forced_reach<<",\"rounds\":"<<rounds<<",\"leaves\":"<<leaves<<",\"elapsed_seconds\":"<<elapsed()<<",\"arcs\":[";
 if(found){bool first=true;for(int u=0;u<n;++u)for(int v=0;v<n;++v)if(model.a[u][v]){if(!first)cout<<",";first=false;cout<<"["<<u<<","<<v<<","<<model.a[u][v]-1<<"]";}}
 cout<<"]}\n";return stopped?2:0;
 }catch(const exception&e){cerr<<e.what()<<"\n";return 1;}}
