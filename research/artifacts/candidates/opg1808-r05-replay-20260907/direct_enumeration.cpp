// Candidate-only exhaustive labelled tournaments; no F-cycle/reach proxy/SAT.
// Fix first arc 0->1 of colour 0; label-swap x colour-swap gives weight 6.
#include <array>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>
using namespace std;
int n,m; int e[6][6]; vector<pair<int,int>> pairs;
uint64_t checked=0,rejected=0,nodes=0,bad=0;array<uint64_t,7> histogram{};
array<uint64_t,16> six{}; bool incomplete=false,closure_disagreement=false;
vector<array<int,3>> tight;int min_sources=7;
chrono::steady_clock::time_point start;
double limit_seconds;
bool time_up(){return chrono::duration<double>(chrono::steady_clock::now()-start).count()>limit_seconds;}
void leaf(){
 ++checked;unsigned adj[3][6]{};
 for(auto [u,v]:pairs){if(e[u][v]>=0)adj[e[u][v]][u]|=1u<<v;else adj[e[v][u]][v]|=1u<<u;}
 unsigned fw[3][6]{};
 for(int c=0;c<3;++c)for(int u=0;u<n;++u)fw[c][u]=adj[c][u]|(1u<<u);
 for(int c=0;c<3;++c)for(int k=0;k<n;++k)for(int u=0;u<n;++u)if(fw[c][u]&(1u<<k))fw[c][u]|=fw[c][k];
 int sources=0;
 for(int s=0;s<n;++s){unsigned total=0;
  for(int c=0;c<3;++c){unsigned visited=1u<<s;int queue[6],head=0,tail=1;queue[0]=s;
   while(head<tail){unsigned next=adj[c][queue[head++]]&~visited;while(next){int v=__builtin_ctz(next);next&=next-1;visited|=1u<<v;queue[tail++]=v;}}
   if(visited!=fw[c][s]){closure_disagreement=true;return;}total|=visited;
  }
  if(total==((1u<<n)-1))++sources;
 }
 ++histogram[sources];if(!sources)++bad;
 if(sources<min_sources){min_sources=sources;tight.clear();for(auto [u,v]:pairs){if(e[u][v]>=0)tight.push_back({u,v,e[u][v]});else tight.push_back({v,u,e[v][u]});}}
}
void dfs(int d){
 if(incomplete||closure_disagreement||bad)return;
 ++nodes;if((nodes&16383)==0&&time_up()){incomplete=true;return;}
 if(d==m){leaf();return;}
 auto [a,b]=pairs[d];
 for(int dir=0;dir<2;++dir){int u=dir?b:a,v=dir?a:b;
  for(int c=0;c<3;++c){
   e[u][v]=c;e[v][u]=-1;bool rainbow=false;
   for(int w=0;w<n;++w)if(w!=u&&w!=v&&e[v][w]>=0&&e[w][u]>=0&&e[v][w]!=c&&e[w][u]!=c&&e[v][w]!=e[w][u])rainbow=true;
   if(rainbow)rejected+=six[m-d-1];else dfs(d+1);
   e[u][v]=e[v][u]=-1;
   if(incomplete||closure_disagreement||bad)return;
  }
 }
}
int main(int argc,char**argv){try{
 if(argc!=3)throw invalid_argument("N TIMEOUT_SECONDS");n=stoi(argv[1]);limit_seconds=stod(argv[2]);if(n<1||n>5||limit_seconds<=0||limit_seconds>30)throw invalid_argument("bounds");
 for(auto&r:e)for(auto&x:r)x=-1;
 for(int u=0;u<n;++u)for(int v=u+1;v<n;++v)pairs.push_back({u,v});m=pairs.size();six[0]=1;for(int i=1;i<16;++i)six[i]=six[i-1]*6;
 start=chrono::steady_clock::now();if(n>1){e[0][1]=0;dfs(1);}else dfs(0);
 uint64_t weight=n>1?6:1,total=six[m];
 string status=incomplete?"incomplete":closure_disagreement?"bfs_floyd_closure_disagreement":bad?"counterexample_candidate":"exhausted_no_counterexample";
 if(!incomplete&&!closure_disagreement&&!bad&&weight*(checked+rejected)!=total)throw logic_error("coverage count closure_disagreement");
 cout<<"{\"n\":"<<n<<",\"status\":\""<<status<<"\",\"palette\":3,\"normalization_weight\":"<<weight<<",\"representatives_checked\":"<<checked<<",\"rainbow_rejected_representatives\":"<<rejected<<",\"all_labelled_assignments\":"<<total<<",\"rainbow_free_assignments\":"<<weight*checked<<",\"nodes\":"<<nodes<<",\"counterexamples\":"<<bad<<",\"timeout_seconds\":"<<limit_seconds<<",\"seconds\":"<<chrono::duration<double>(chrono::steady_clock::now()-start).count()<<",\"monosource_histogram_labelled\":[";
 for(int i=0;i<=n;++i){if(i)cout<<",";cout<<weight*histogram[i];}cout<<"],\"minimum_monosources\":"<<min_sources<<",\"tight_arcs\":[";
 for(size_t i=0;i<tight.size();++i){if(i)cout<<",";auto a=tight[i];cout<<"["<<a[0]<<","<<a[1]<<","<<a[2]<<"]";}cout<<"]}\n";
 return incomplete?2:closure_disagreement?3:bad?4:0;
 }catch(exception&e){cerr<<e.what()<<"\n";return 1;}}
