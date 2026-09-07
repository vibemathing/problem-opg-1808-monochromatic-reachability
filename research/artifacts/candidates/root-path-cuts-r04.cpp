// Candidate-only dominator/bridge propagation on potential PHYSICAL paths.
#define main r03_entry
#include "root-interval-search-r03.cpp"
#undef main
uint64_t cut_tests=0,cut_reject=0,cut_arcs=0,cut_reaches=0;
int cut_level=3; // bit 1: internal vertex; bit 2: internal edge
int path_cuts(State&s,const vector<Domain>&ds){
 Bits adj[K][M]{};
 for(auto[u,v]:pairs){if(s.a[u][v])adj[s.a[u][v]-1][u]|=bit(v);if(s.a[v][u])adj[s.a[v][u]-1][v]|=bit(u);}
 for(const auto&d:ds)for(auto q:d.choices)adj[q.c][q.u]|=bit(q.v);
 for(int u=0;u<n;++u)for(int v=0;v<n;++v){
  if(u==v||v==pred(u))continue;
  Bits mask=intervals[u][v];int count=0,c=-1;
  for(int col=0;col<k;++col)if(possible_reach(s,u,v,col)&&(reachable(adj[col],u,mask)&bit(v))){++count;c=col;}
  if(count!=1)continue;
  // Every mandatory edge/vertex lies on any one chosen potential simple path.
  int parent[M];fill(parent,parent+M,-1);parent[u]=u;vector<int>queue{u};
  for(size_t j=0;j<queue.size()&&parent[v]<0;++j){int x=queue[j];Bits next=adj[c][x]&mask;
   while(next){int y=__builtin_ctz(next);next&=next-1;if(parent[y]<0){parent[y]=x;queue.push_back(y);}}
  }
  if(parent[v]<0)throw logic_error("lost physical support");
  vector<int>path{v};while(path.back()!=u)path.push_back(parent[path.back()]);reverse(path.begin(),path.end());
  if(cut_level&1)for(size_t j=1;j+1<path.size();++j){int w=path[j];
   if((s.lo[c][u]&bit(w))&&(s.lo[c][w]&bit(v)))continue;
   ++cut_tests;if(reachable(adj[c],u,mask&~bit(w))&bit(v))continue;
   for(auto[x,y]:vector<pair<int,int>>{{u,w},{w,v}})if(!(s.lo[c][x]&bit(y))){
    if(!possible_reach(s,x,y,c)){++cut_reject;return -1;}
    insert_reach(s,x,y,c);++cut_reaches;
   }
   return 1;
  }
  if(cut_level&2)for(size_t j=1;j<path.size();++j){int x=path[j-1],y=path[j];
   if(s.a[x][y])continue;
   ++cut_tests;adj[c][x]&=~bit(y);bool avoid=bool(reachable(adj[c],u,mask)&bit(v));adj[c][x]|=bit(y);
   if(avoid)continue;
   if(!insert_arc(s,{x,y,c})){++cut_reject;return -1;}
   ++cut_arcs;return 1;
  }
 }
 return 0;
}
bool cut_propagate(State&s,vector<Domain>&ds){
 for(;;){if(!propagate(s,ds))return false;int r=path_cuts(s,ds);if(r<0)return false;if(!r)return true;}
}
void cut_dfs(State s){
 if(stopped||found)return;
 ++nodes;if(nodes>node_limit||(nodes%32==0&&elapsed()>seconds_limit)){stopped=true;return;}
 vector<Domain>ds;if(!cut_propagate(s,ds))return;
 if(ds.empty()){if(!audit(s))throw logic_error("cut physical audit failed");model=s;found=true;return;}
 auto best=min_element(ds.begin(),ds.end(),[](const Domain&a,const Domain&b){return a.choices.size()<b.choices.size();});
 for(Arc q:best->choices){State t=s;if(!insert_arc(t,q))throw logic_error("stale cut domain");cut_dfs(t);if(stopped||found)return;}
}
int main(int argc,char**argv){try{
 if(argc<8||argc>9)throw invalid_argument("N PALETTE FORBID_RAINBOW MODE SECONDS NODE_CAP CYCLE_WORD [CUT_LEVEL]");
 n=stoi(argv[1]);k=stoi(argv[2]);nr=stoi(argv[3]);mode=stoi(argv[4]);seconds_limit=stod(argv[5]);node_limit=stoull(argv[6]);string word=argv[7];
 if(argc==9)cut_level=stoi(argv[8]);
 if(n<3||n>M||k<1||k>K||(nr!=0&&nr!=1)||mode!=2||!(seconds_limit>0)||!node_limit||int(word.size())!=n||cut_level<0||cut_level>3)throw invalid_argument("parameters out of bounds");
 for(char c:word)if(c<'0'||c>='0'+k)throw invalid_argument("invalid colour");
 full=bit(n)-1;for(int u=0;u<n;++u){Bits mask=bit(u);for(int d=1;d<n;++d){int v=(u+d)%n;mask|=bit(v);intervals[u][v]=mask;}}
 for(int u=0;u<n;++u)for(int v=u+1;v<n;++v)pairs.push_back({u,v});
 State s;for(int c=0;c<k;++c)for(int u=0;u<n;++u)s.lo[c][u]=bit(u);
 started=chrono::steady_clock::now();bool ok=true;for(int u=0;u<n;++u)if(!insert_arc(s,{u,(u+1)%n,word[u]-'0'})){ok=false;break;}
 if(ok)cut_dfs(s);
 cout<<"{\"n\":"<<n<<",\"palette\":"<<k<<",\"forbid_rainbow\":"<<nr<<",\"mode\":"<<mode<<",\"cut_level\":"<<cut_level<<",\"word\":\""<<word<<"\",\"status\":\""<<(stopped?"incomplete":found?"witness":"exhausted_no_witness")<<"\",\"nodes\":"<<nodes<<",\"trials\":"<<trials<<",\"cut_tests\":"<<cut_tests<<",\"cut_reject\":"<<cut_reject<<",\"cut_arcs\":"<<cut_arcs<<",\"cut_reaches\":"<<cut_reaches<<",\"seconds\":"<<elapsed()<<",\"arcs\":[";
 if(found){bool first=true;for(int u=0;u<n;++u)for(int v=0;v<n;++v)if(model.a[u][v]){if(!first)cout<<",";first=false;cout<<"["<<u<<","<<v<<","<<model.a[u][v]-1<<"]";}}
 cout<<"]}\n";return stopped?2:0;
 }catch(const exception&e){cerr<<e.what()<<"\n";return 1;}}
