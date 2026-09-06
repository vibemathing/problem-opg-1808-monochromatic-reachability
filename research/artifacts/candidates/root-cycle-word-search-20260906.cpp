// Generator-side finite search, not an admitted verifier.
// Compile: g++ -O2 -std=c++17 root-cycle-search-20260906.cpp -o root-search
// Run: ./root-search N COLOURS NO_RAINBOW TIMEOUT_SECONDS NODE_LIMIT
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <vector>
using namespace std;
constexpr int M=12, K=4;
struct State { int a[M][M]{}; uint16_t r[K][M]{}; int used=0, assigned=0; };
struct Choice {int u,v,c;};
int n,k,nr; uint64_t nodes=0, trials=0, prune_triangle=0, prune_reach=0, dead=0, leaves=0, limit;
bool stopped=false, found=false; double timeout_s; chrono::steady_clock::time_point start;
vector<pair<int,int>> pairs; State model;
bool extend(const State &s,Choice q, State &t) {
 ++trials;
 int u=q.u,v=q.v,c=q.c;
 if(nr) for(int w=0;w<n;++w) if(s.a[v][w] && s.a[w][u]) {
  int x=s.a[v][w]-1,y=s.a[w][u]-1;
  if(c!=x && c!=y && x!=y){++prune_triangle;return false;}
 }
 t=s; t.a[u][v]=c+1; ++t.assigned; t.used=max(t.used,c+1);
 // For an exact reflexive transitive closure R, insertion u->v adds R(*,u) x R(v,*).
 uint16_t succ=s.r[c][v];
 for(int x=0;x<n;++x) if(s.r[c][x] & (1u<<u)) t.r[c][x] |= succ;
 for(int x=0;x<n;++x) if(t.r[c][x] & (1u<<((x+n-1)%n))){++prune_reach;return false;}
 return true;
}
void dfs(const State &s) {
 if(stopped||found)return;
 ++nodes;
 if(nodes>limit || (nodes%1024==0 && chrono::duration<double>(chrono::steady_clock::now()-start).count()>timeout_s)){stopped=true;return;}
 if(s.assigned==int(pairs.size())){++leaves;model=s;found=true;return;}
 vector<Choice> best; int bestn=100;
 for(auto [u,v]:pairs){
  if(s.a[u][v]||s.a[v][u])continue;
  vector<Choice> domain;
  for(int dir=0;dir<2;++dir){
   int x=dir?v:u,y=dir?u:v;
   // All arcs on 0->1->...->n-1->0 have fixed forward orientation.
   if((y+1)%n==x)continue;
   for(int c=0;c<min(k,s.used+1);++c){State t;Choice q{x,y,c};if(extend(s,q,t))domain.push_back(q);}
  }
  if(domain.empty()){++dead;return;}
  if(int(domain.size())<bestn){best=domain;bestn=int(domain.size());}
 }
 for(Choice q:best){State t;if(!extend(s,q,t))throw logic_error("domain changed");dfs(t);if(stopped||found)return;}
}
int main(int argc,char**argv){
 try {
 if(argc!=6 && argc!=7)throw invalid_argument("arguments: N COLOURS NO_RAINBOW TIMEOUT_SECONDS NODE_LIMIT");
 n=stoi(argv[1]);k=stoi(argv[2]);nr=stoi(argv[3]);timeout_s=stod(argv[4]);limit=stoull(argv[5]);
 if(n<3||n>M||k<1||k>K||(nr!=0&&nr!=1)||timeout_s<=0||limit==0)throw invalid_argument("out of range");
 State s; for(int c=0;c<k;++c)for(int v=0;v<n;++v)s.r[c][v]=1u<<v;
 for(int u=0;u<n;++u)for(int v=u+1;v<n;++v)pairs.push_back({u,v});
 start=chrono::steady_clock::now();
 bool prefix_ok=true;
 if(argc==7){string word=argv[6];if(int(word.size())!=n)throw invalid_argument("prefix length");
  for(int i=0;i<n;++i){int c=word[i]-'0';if(c<0||c>=k)throw invalid_argument("prefix colour");
   State t;if(!extend(s,{i,(i+1)%n,c},t)){prefix_ok=false;break;}s=t;
  }
 }
 if(prefix_ok)dfs(s);
 double elapsed=chrono::duration<double>(chrono::steady_clock::now()-start).count();
 cout<<"{\"cycle_word\":\""<<(argc==7?argv[6]:"")<<"\",\"n\":"<<n<<",\"palette\":"<<k<<",\"no_rainbow\":"<<(nr?"true":"false")<<",\"status\":\""<<(stopped?"incomplete":found?"witness":"exhausted_no_witness")<<"\",\"nodes\":"<<nodes<<",\"trials\":"<<trials<<",\"triangle_rejections\":"<<prune_triangle<<",\"reach_rejections\":"<<prune_reach<<",\"dead_nodes\":"<<dead<<",\"leaves\":"<<leaves<<",\"elapsed_seconds\":"<<elapsed<<",\"arcs\":[";
 if(found){bool first=true;for(int u=0;u<n;++u)for(int v=0;v<n;++v)if(model.a[u][v]){if(!first)cout<<",";first=false;cout<<"["<<u<<","<<v<<","<<model.a[u][v]-1<<"]";}}
 cout<<"]}\n";return stopped?2:0;
 }catch(const exception&e){cerr<<e.what()<<"\n";return 1;}
}
