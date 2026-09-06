// Fixed-order, all-labelled-colour reference enumeration; same generator trust domain.
#include <array>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <string>
#include <vector>
using namespace std;
int n,k,nr; int a[12][12]{}; vector<pair<int,int>> edges;
uint64_t nodes=0, leaves=0; bool stop=false,found=false;
chrono::steady_clock::time_point start; double budget;
bool ok(){
 if(nr)for(int x=0;x<n;++x)for(int y=0;y<n;++y)if(a[x][y])for(int z=0;z<n;++z)
  if(a[y][z]&&a[z][x]&&a[x][y]!=a[y][z]&&a[x][y]!=a[z][x]&&a[y][z]!=a[z][x])return false;
 for(int c=1;c<=k;++c){bool r[12][12]{};
  for(int u=0;u<n;++u)for(int v=0;v<n;++v)r[u][v]=(u==v||a[u][v]==c);
  for(int w=0;w<n;++w)for(int u=0;u<n;++u)for(int v=0;v<n;++v)r[u][v]=r[u][v]||(r[u][w]&&r[w][v]);
  for(int u=0;u<n;++u)if(r[u][(u+n-1)%n])return false;
 }return true;
}
void visit(int d){
 if(stop||found)return; ++nodes;
 if(nodes%1024==0&&chrono::duration<double>(chrono::steady_clock::now()-start).count()>budget){stop=true;return;}
 if(d==int(edges.size())){++leaves;found=true;return;}
 auto [u,v]=edges[d];
 for(int dir=0;dir<2;++dir){int x=dir?v:u,y=dir?u:v;if((y+1)%n==x)continue;
  for(int c=1;c<=(d==0?1:k);++c){a[x][y]=c;if(ok())visit(d+1);a[x][y]=0;if(stop||found)return;}
 }
}
int main(int argc,char**argv){
 if(argc!=5)return 1; n=stoi(argv[1]);k=stoi(argv[2]);nr=stoi(argv[3]);budget=stod(argv[4]);
 if(n<3||n>10||k<1||k>4||budget<=0||(nr!=0&&nr!=1))return 1;
 for(int u=0;u<n;++u)for(int v=u+1;v<n;++v)edges.push_back({u,v});
 start=chrono::steady_clock::now();visit(0);
 cout<<"{\"n\":"<<n<<",\"palette\":"<<k<<",\"no_rainbow\":"<<(nr?"true":"false")<<",\"status\":\""<<(stop?"incomplete":found?"witness":"exhausted_no_witness")<<"\",\"nodes\":"<<nodes<<",\"leaves\":"<<leaves<<",\"seconds\":"<<chrono::duration<double>(chrono::steady_clock::now()-start).count()<<"}\n";
 return stop?2:0;
}
