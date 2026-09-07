// Candidate extension of R03. Reuse the frozen R03 source next to this file.
#define main r03_entry
#include "root-interval-search-r03.cpp"
#undef main
uint64_t subset_tests=0,subset_reject=0,subset_forces=0;
vector<Bits> tested_subsets;
int subset_level=2;
// Every real completion path remains in the potential PHYSICAL graph.
unsigned colours(const State&s,const Bits adj[K][M],Bits mask,int u,int v){
 unsigned out=0;
 for(int c=0;c<k;++c)if(possible_reach(s,u,v,c)&&(reachable(adj[c],u,mask)&bit(v)))out|=1u<<c;
 return out;
}
// Return -1 on contradiction, 1 on a new fact, 0 otherwise.
int requirement(State&s,const Bits adj[K][M],const Bits rev[K][M],Bits mask,int u,int v){
 unsigned options=colours(s,adj,mask,u,v);
 if(!options)return -1;
 if(__builtin_popcount(options)!=1)return 0;
 int c=__builtin_ctz(options);
 if(!(s.lo[c][u]&bit(v))){insert_reach(s,u,v,c);++subset_forces;return 1;}
 Bits first=adj[c][u]&mask&reachable(rev[c],v,mask&~bit(u));
 Bits last=rev[c][v]&mask&reachable(adj[c],u,mask&~bit(v));
 if(!first||!last)return -1;
 Arc q{-1,-1,c};
 if(__builtin_popcount(first)==1){int w=__builtin_ctz(first);if(!s.a[u][w])q={u,w,c};}
 if(q.u<0&&__builtin_popcount(last)==1){int w=__builtin_ctz(last);if(!s.a[w][v])q={w,v,c};}
 if(q.u<0)return 0;
 if(!insert_arc(s,q))return -1;
 ++subset_forces;return 1;
}
int subset_pass(State&s,const vector<Domain>&ds){
 Bits adj[K][M]{},rev[K][M]{};
 for(auto[u,v]:pairs){
  if(s.a[u][v]){int c=s.a[u][v]-1;adj[c][u]|=bit(v);rev[c][v]|=bit(u);}
  if(s.a[v][u]){int c=s.a[v][u]-1;adj[c][v]|=bit(u);rev[c][u]|=bit(v);}
 }
 for(const auto&d:ds)for(auto q:d.choices){adj[q.c][q.u]|=bit(q.v);rev[q.c][q.v]|=bit(q.u);}
 for(Bits mask:tested_subsets){
  ++subset_tests;
  Bits starts=mask&~(((mask<<1)&full)|(mask>>(n-1)));
  Bits ends=mask&~((mask>>1)|((mask&1)<<(n-1)));
  for(int direction=0;direction<2;++direction){
   Bits candidates=direction?ends:starts,valid=0;
   while(candidates){int x=__builtin_ctz(candidates);candidates&=candidates-1;
    bool ok=true;Bits targets=mask&~bit(x);
    while(targets&&ok){int y=__builtin_ctz(targets);targets&=targets-1;
     if(!colours(s,adj,mask,direction?y:x,direction?x:y))ok=false;
    }
    if(ok)valid|=bit(x);
   }
   if(!valid){++subset_reject;return -1;}
   if(__builtin_popcount(valid)!=1)continue;
   int x=__builtin_ctz(valid);Bits targets=mask&~bit(x);
   while(targets){int y=__builtin_ctz(targets);targets&=targets-1;
    int r=requirement(s,adj,rev,mask,direction?y:x,direction?x:y);
    if(r<0)++subset_reject;
    if(r)return r;
   }
  }
 }
 return 0;
}
bool strong_propagate(State&s,vector<Domain>&ds){
 for(;;){if(!propagate(s,ds))return false;int r=subset_pass(s,ds);if(r<0)return false;if(!r)return true;}
}
bool subset_audit(const State&s){
 if(!audit(s))return false;
 Bits adj[K][M]{};
 for(int u=0;u<n;++u)for(int v=0;v<n;++v)if(s.a[u][v])adj[s.a[u][v]-1][u]|=bit(v);
 for(Bits mask:tested_subsets){bool source=false,sink=false;
  for(int x=0;x<n;++x)if(mask&bit(x)){
   Bits all=0;for(int c=0;c<k;++c)all|=reachable(adj[c],x,mask);if(all==mask)source=true;
   bool ok=true;for(int y=0;y<n;++y)if(mask&bit(y)){
    bool got=false;for(int c=0;c<k;++c)if(reachable(adj[c],y,mask)&bit(x))got=true;
    if(!got)ok=false;
   }
   if(ok)sink=true;
  }
  if(!source||!sink)return false;
 }
 return true;
}
void strong_dfs(State s){
 if(stopped||found)return;
 ++nodes;if(nodes>node_limit||(nodes%32==0&&elapsed()>seconds_limit)){stopped=true;return;}
 vector<Domain>ds;if(!strong_propagate(s,ds))return;
 if(ds.empty()){if(!subset_audit(s))throw logic_error("subset physical audit failed");model=s;found=true;return;}
 auto best=min_element(ds.begin(),ds.end(),[](const Domain&a,const Domain&b){return a.choices.size()<b.choices.size();});
 for(Arc q:best->choices){State t=s;if(!insert_arc(t,q))throw logic_error("stale strong domain");strong_dfs(t);if(stopped||found)return;}
}
void make_subsets(){
 for(Bits mask=1;mask<full;++mask){
  int missing=n-__builtin_popcount(mask);
  Bits starts=mask&~(((mask<<1)&full)|(mask>>(n-1)));
  if(__builtin_popcount(starts)<2)continue; // single intervals already covered
  if(subset_level==0)continue;
  if(subset_level==2&&missing!=2)continue;
  if(subset_level==3&&missing>3)continue;
  tested_subsets.push_back(mask);
 }
}
int main(int argc,char**argv){try{
 if(argc<8||argc>9)throw invalid_argument("N PALETTE FORBID_RAINBOW MODE SECONDS NODE_CAP CYCLE_WORD [SUBSET_LEVEL]");
 n=stoi(argv[1]);k=stoi(argv[2]);nr=stoi(argv[3]);mode=stoi(argv[4]);seconds_limit=stod(argv[5]);node_limit=stoull(argv[6]);string word=argv[7];
 if(argc==9)subset_level=stoi(argv[8]);
 if(n<3||n>12||k<1||k>K||(nr!=0&&nr!=1)||mode!=2||!(seconds_limit>0)||!node_limit||int(word.size())!=n||subset_level<0||subset_level>4||subset_level==1)throw invalid_argument("parameters out of bounds");
 for(char c:word)if(c<'0'||c>='0'+k)throw invalid_argument("invalid colour");
 full=bit(n)-1;for(int u=0;u<n;++u){Bits mask=bit(u);for(int d=1;d<n;++d){int v=(u+d)%n;mask|=bit(v);intervals[u][v]=mask;}}
 for(int u=0;u<n;++u)for(int v=u+1;v<n;++v)pairs.push_back({u,v});
 make_subsets();
 State s;for(int c=0;c<k;++c)for(int u=0;u<n;++u)s.lo[c][u]=bit(u);
 started=chrono::steady_clock::now();bool ok=true;for(int u=0;u<n;++u)if(!insert_arc(s,{u,(u+1)%n,word[u]-'0'})){ok=false;break;}
 if(ok)strong_dfs(s);
 cout<<"{\"n\":"<<n<<",\"palette\":"<<k<<",\"forbid_rainbow\":"<<nr<<",\"mode\":"<<mode<<",\"subset_level\":"<<subset_level<<",\"word\":\""<<word<<"\",\"status\":\""<<(stopped?"incomplete":found?"witness":"exhausted_no_witness")<<"\",\"nodes\":"<<nodes<<",\"trials\":"<<trials<<",\"subset_tests\":"<<subset_tests<<",\"subset_reject\":"<<subset_reject<<",\"subset_forces\":"<<subset_forces<<",\"seconds\":"<<elapsed()<<",\"arcs\":[";
 if(found){bool first=true;for(int u=0;u<n;++u)for(int v=0;v<n;++v)if(model.a[u][v]){if(!first)cout<<",";first=false;cout<<"["<<u<<","<<v<<","<<model.a[u][v]-1<<"]";}}
 cout<<"]}\n";return stopped?2:0;
 }catch(const exception&e){cerr<<e.what()<<"\n";return 1;}}
