// Positive-fragment calibration of the search; same generator trust domain.
#define main search_entry
#include "root-interval-search-r03.cpp"
#undef main
#include <numeric>
int main(){try{
 n=6;k=4;nr=1;mode=2;full=bit(n)-1;
 for(int u=0;u<n;++u){Bits mask=bit(u);for(int d=1;d<n;++d){int v=(u+d)%n;mask|=bit(v);intervals[u][v]=mask;}}
 for(int u=0;u<n;++u)for(int v=u+1;v<n;++v)pairs.push_back({u,v});
 vector<Arc> fixture={{0,1,0},{0,2,1},{1,2,2},{1,3,3},{1,4,0},{2,3,1},{2,4,3},{2,5,0},{3,0,0},{3,4,0},{3,5,3},{4,0,3},{4,5,2},{5,0,1},{5,1,2}};
 uint64_t checked=0;array<int,4> permutation={0,1,2,3};
 do{for(int shift=0;shift<n;++shift){
  State target;vector<Arc>cycle,chords;Bits real[K][M]{};
  for(int c=0;c<k;++c)for(int u=0;u<n;++u)real[c][u]=bit(u);
  for(auto q:fixture){q={(q.u+shift)%n,(q.v+shift)%n,permutation[q.c]};target.a[q.u][q.v]=q.c+1;
   real[q.c][q.u]|=bit(q.v);((q.v==(q.u+1)%n)?cycle:chords).push_back(q);}
  // Reference closure recomputed by Floyd-Warshall from physical fixture arcs.
  for(int c=0;c<k;++c)for(int z=0;z<n;++z)for(int u=0;u<n;++u)
   if(real[c][u]&bit(z))real[c][u]|=real[c][z];
  if(!audit(target))throw logic_error("fixture not in required domain");
  for(unsigned mask=0;mask<(1u<<chords.size());++mask){
   State s;for(int c=0;c<k;++c)for(int u=0;u<n;++u)s.lo[c][u]=bit(u);
   for(auto q:cycle)if(!insert_arc(s,q))throw logic_error("cycle rejected");
   for(unsigned j=0;j<chords.size();++j)if(mask&(1u<<j))if(!insert_arc(s,chords[j]))throw logic_error("fragment rejected");
   vector<Domain>ds;if(!propagate(s,ds))throw logic_error("feasible fragment pruned");
   for(int u=0;u<n;++u)for(int v=0;v<n;++v)if(s.a[u][v]&&s.a[u][v]!=target.a[u][v])throw logic_error("false forced arc");
   for(int c=0;c<k;++c)for(int u=0;u<n;++u)if(s.lo[c][u]&~real[c][u])throw logic_error("false forced reach");
   ++checked;
  }
 }}while(next_permutation(permutation.begin(),permutation.end()));
 cout<<"{\"calibration\":\"four_colour_physical_fixture_fragments\",\"checked_states\":"<<checked<<",\"vertex_rotations\":6,\"colour_permutations\":24,\"chord_subsets_each\":512,\"all_preserved\":true,\"verdict\":\"candidate_only\"}\n";
 return 0;
 }catch(const exception&e){cerr<<e.what()<<"\n";return 1;}}
