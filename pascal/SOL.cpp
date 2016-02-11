
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <cstdlib>
#include <vector>
#include <cmath>
#include <algorithm>
#include <thread>
#include <mutex>
#include <set>

//#include "Graph.h"

using namespace std;


int X, Y, D, T, M, O, P, W;
vector<int> PW, WX, WY, TX, TY;

vector<vector<int>> STOCK;
vector<vector<int>> ORDER;

vector<int> DX, DY, DT;

vector<vector<int>> SOLUTION;

int dist(int x1, int y1, int x2, int y2) {
  int dx = x1-x2;
  int dy = y1-y2;
  return ceil(sqrt(dx*dx+dy*dy));
}


void load_data(const char* str) {

  ifstream F;
  F.open(str);

  F >> X >> Y >> D >> T >> M;

  DX.resize(D);
  DY.resize(D);
  DT.resize(D);


  F >> P;
  PW.resize(P);
  for(int i = 0; i < P; i++)
    F >> PW[i]; 
  F >> W;
  WX.resize(W);
  WY.resize(W);
  STOCK.resize(W);
  for(int i = 0; i < W; i++) {
    STOCK[i].resize(P);
    F >> WX[i] >> WY[i];
    for(int j = 0; j < P; j++)
      F >> STOCK[i][j];
  }
  F >> O;
  TX.resize(O);
  TY.resize(O);
  ORDER.resize(O);
  for(int i = 0; i < O; i++) {
    F >> TX[i] >> TY[i];
    int c;
    F >> c;
    ORDER[i].resize(c);
    for(int j = 0; j < c; j++) F >> ORDER[i][j];
  }


  for(int i = 0; i < D; i++) {
    DX[i] = WX[0];
    DY[i] = WY[0];
    DT[i] = 0;
  }


}






bool load_product(int drone, int warehouse, int type) {
  DT[drone] += dist(DX[drone], DY[drone], WX[warehouse], WY[warehouse]) + 1;
  DX[drone] = WX[warehouse];
  DY[drone] = WY[warehouse];

  if(DT[drone] >= T) return false;
  STOCK[warehouse][type]--;

  SOLUTION.push_back(vector<int>{drone, 0, warehouse, type, 1});
//  cout << drone << " L " << warehouse << " " << type << " 1" << endl;
  return true;
}

bool deliver_product(int drone, int order, int type) {
  DT[drone] += dist(DX[drone], DY[drone], TX[order], TY[order]) + 1;
  DX[drone] = TX[order];
  DY[drone] = TY[order];

  if(DT[drone] >= T) return false;
  SOLUTION.push_back(vector<int>{drone, 1, order, type, 1});  
//  cout << drone << " D " << order << " " << type << " 1" << endl;
  return true;
}


int find_nearest_warehouse(int x, int y, int type) {
  int best = 100000;
  int best_w = 0;
  for(int i = 0; i < W; i++)
    if(STOCK[i][type] > 0 && dist(x, y, WX[i], WY[i]) < best) {
      best = dist(x, y, WX[i], WY[i]);
      best_w = i;
    }
  return best_w;
}


bool deliver_order(int order, int drone) {

  for(int i = 0; i < ORDER[order].size(); i++) {
    int type = ORDER[order][i];
    int w = find_nearest_warehouse(DX[drone], DY[drone], type);
    if(!load_product(drone, w, type)) return false;
    if(!deliver_product(drone, order, type)) return false;
  }
  return true;
}


void print_solution(vector<vector<int>> &SOL) {
  cout << SOL.size() << endl;
  for(int i = 0; i < SOL.size(); i++) {
    cout << SOL[i][0] << ' ';
    switch(SOL[i][1]) {
      case 0: cout << "L "; break;
      case 1: cout << "D "; break;
    }
    cout << SOL[i][2] << ' ' << SOL[i][3] << ' ' << SOL[i][4] << endl;
  }
}


int main(int argc, const char** argv) {
  srand(time(0)); 
  if(argc > 1) load_data(argv[1]);

  for(int i = 0; i < O; i++) 
    if(!deliver_order(i, 0)) break;

  print_solution(SOLUTION);
}
