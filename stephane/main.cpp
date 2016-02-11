#include <iostream>
#include <fstream>
#include <cassert>
#include <vector>
#include <cstring>
#include <cmath>
#include <sstream>
#include <iomanip>
#include <algorithm>
#include <unistd.h>
#include "Visu.h"

using namespace std;

uint32_t seed = 123456789; double nextDouble() { return (1./~((uint32_t)0)) * (seed = 1664525 * seed + 1013904223); } uint32_t nextInt(int m) { return m * (1./~((uint32_t)0)) * (seed = 1664525 * seed + 1013904223); }

string outputdir;
int score;

#define MAXX 300
#define MAXY 500
#define MAXD 30
#define MAXT 145416
#define MAXM 200
#define MAXP 2000
#define MAXW 16
#define MAXO 1250

int X;
int Y;
int D;
int T;
int M;
int P;
int W;
int O;

int stockbackup[MAXW][MAXP];

int weight[MAXP];
int stock[MAXW][MAXP];
int wx[MAXW];
int wy[MAXW];

int ox[MAXO];
int oy[MAXO];
vector<int> oprod[MAXO];
int oflatprod[MAXP];
int oflatprodbis[MAXP];

int dx[MAXD];
int dy[MAXD];
vector<int> dorders[MAXD];

#define LOAD 1
#define DELIVER 2

struct Command
{
    int type;
    int drone;
    int target;
    int prod;
    int quantity;
};

vector<Command> commands;

int dist(int x1, int y1, int x2, int y2)
{
    double dx = x1-x2;
    double dy = y1-y2;
    return sqrt(dx*dx+dy*dy);
}

// void render()
// {
//     glBegin(GL_QUADS);
//     glColor3f(0, 0, 0);
//     glVertex2f(0, 0);
//     glVertex2f(0, Y);
//     glVertex2f(X, Y);
//     glVertex2f(X, 0);
//     glEnd();

//     for (int o = 0; o < O; ++o)
//     {
//         int x = ox[o];
//         int y = oy[o];
//         glBegin(GL_QUADS);
//         glColor3f(0, 1, 0);
//         glVertex2f(x, y);
//         glVertex2f(x, y+2);
//         glVertex2f(x+2, y+2);
//         glVertex2f(x+2, y);
//         glEnd();
//     }


//     for (int w = 0; w < W; ++w)
//     {
//         int x = wx[w];
//         int y = wy[w];
//         glBegin(GL_QUADS);
//         glColor3f(1, 0, 0);
//         glVertex2f(x, y);
//         glVertex2f(x, y+3);
//         glVertex2f(x+3, y+3);
//         glVertex2f(x+2, y);
//         glEnd();
//     }

//     for (int d = 0; d < D; ++d)
//     {
//         int x = dx[d];
//         int y = dy[d];
//         glBegin(GL_QUADS);
//         glColor3f(0, 0, 1);
//         glVertex2f(x, y);
//         glVertex2f(x, y+5);
//         glVertex2f(x+5, y+5);
//         glVertex2f(x+5, y);
//         glEnd();
//     }
// }

void readInput(const string & filename)
{
    ifstream in(filename);
    in >> X >> Y >> D >> T >> M;
    in >> P;
    for (int p = 0; p < P; ++p)
        in >> weight[p];
    in >> W;
    for (int w = 0; w < W; ++w)
    {
        in >> wx[w] >> wy[w];
        for (int p = 0; p < P; ++p)
            in >> stockbackup[w][p];
    }
    in >> O;
    for (int o = 0; o < O; ++o)
    {
        in >> ox[o] >> oy[o];
        int nbprod;
        in >> nbprod;
        for (int n = 0; n < nbprod; ++n)
        {
            int prod = 0;
            in >> prod;
            oprod[o].push_back(prod);
        }
    }
}

double wscore[MAXW];
double oscore[MAXO];

struct Sorter
{
    bool operator()(int l, int r) const
    {
        return wscore[l] > wscore[r];
    }
};

struct Bob
{
    bool operator()(int l, int r) const
    {
        return oscore[l] < oscore[r];
    }
};

string getfilename(int score)
{
    stringstream ss;
    ss << outputdir << "/res_" << setprecision(2) << setw(10) << fixed << setfill('0') << score;
    return ss.str();
}

void writeOutput()
{
    ofstream out(getfilename(score));
    out << (int)commands.size() << endl;
    for (int c = 0; c < (int)commands.size(); ++c)
    {
        switch (commands[c].type)
        {
        case LOAD:
            out << commands[c].drone << " L " << commands[c].target << " " << commands[c].prod << " " << commands[c].quantity << endl;
            break;
        case DELIVER:
            out << commands[c].drone << " D " << commands[c].target << " " << commands[c].prod << " " << commands[c].quantity << endl;
            break;
        }
    }
}

void solve()
{
    int bestscore = 0;
    for (int d = 0; d < D; ++d)
        dorders[d].clear();

    int alice[O];
    for (int o = 0; o < O; ++o)
    {
        alice[o] = o;
        oscore[o] = 0;
        for (int p = 0; p < (int)oprod[o].size(); ++p)
            oscore[o] += 1000 + weight[oprod[o][p]];
        int avgdist = 0;
        for (int w = 0; w < W; ++w)
            avgdist += dist(wx[w], wy[w], ox[o], oy[o]);
        avgdist /= W;
        oscore[o] *= avgdist;
    }

    sort(alice, alice+O, Bob());

    for (int oi = 0; oi < O; ++oi)
    {
        int o = alice[oi];
        dorders[nextInt(D)].push_back(o);
    }

    // for (int k = 0; k < 100; ++k)
    {
        commands.clear();
        for (int d = 0; d < D; ++d)
        {
            dx[d] = wx[0];
            dy[d] = wy[0];
        }

        for (int w = 0; w < W; ++w)
            for (int p = 0; p < P; ++p)
                stock[w][p] = stockbackup[w][p];

        score = 0;

        // Visu::display();

        // int d = 0;
        for (int d = 0; d < D; ++d)
        {
            int t = 0;

            // int oi = 0;
            for (int oi = 0; oi < (int)dorders[d].size(); ++oi)
            {
                int o = dorders[d][oi];
                memset(&oflatprod, 0, sizeof(oflatprod));
                memset(&oflatprodbis, 0, sizeof(oflatprodbis));
                int totalprod = 0;
                for (int op = 0; op < (int)oprod[o].size(); ++op)
                {
                    // cout << __func__ << ":" << __LINE__ << " " << oprod[o][op] << endl;
                    ++totalprod;
                    ++oflatprod[oprod[o][op]];
                }
                // if (totalprod == 0)
                // continue;
                // exit(0);

                do
                {
                    // cout << __func__ << ":" << __LINE__ << " " << totalprod << endl;
                    int worder[W];
                    for (int w = 0; w < W; ++w)
                    {
                        worder[w] = w;
                        wscore[w] = 0;
                        for (int p = 0; p < P; ++p)
                            wscore[w] += min(oflatprod[p], stock[w][p]);
                        wscore[w] /= dist(wx[w], wy[w], ox[o], oy[o]);
                    }
                    sort(worder, worder+W, Sorter());
                    // for (int w = 0; w < W; ++w)
                    // cout << worder[w] << " " << wscore[worder[w]] << endl;
                    // cout << endl;
                    int w = worder[0];
                    int cargo = M;
                    for (int p = 0; p < P; ++p)
                    {
                        int q = min(oflatprod[p], stock[w][p]);
                        q = min(q, cargo/weight[p]);
                        if (q > 0)
                        {
                            totalprod -= q;
                            oflatprod[p] -= q;
                            oflatprodbis[p] += q;
                            stock[w][p] -= q;
                            cargo -= q * weight[p];
                            t += 1+dist(dx[d], dy[d], wx[w], wy[w]);
                            // cout << __func__ << ":" << __LINE__ << " " << t << endl;
                            if (t > T) goto timeout;
                            // cout << __func__ << ":" << __LINE__ << " " << 1+dist(dx[d], dy[d], wx[w], wy[w]) << endl;
                            commands.push_back({LOAD, d, w, p, q});
                            // cout << dx[d] << " " << dy[d] << " " << wx[w] << " " << wy[w] << endl;
                            dx[d] = wx[w];
                            dy[d] = wy[w];
                            // Visu::display();
                        }
                    }

                    for (int p = 0; p < P; ++p)
                    {
                        if (oflatprodbis[p] > 0)
                        {
                            t += 1+dist(dx[d], dy[d], ox[o], oy[o]);
                            if (t > T) goto timeout;
                            commands.push_back({DELIVER, d, o, p, oflatprodbis[p]});
                            // cout << dx[d] << " " << dy[d] << " " << ox[o] << " " << oy[o] << endl;
                            dx[d] = ox[o];
                            dy[d] = oy[o];
                            oflatprodbis[p] = 0;
                            // Visu::display();
                        }
                    }
                } while (totalprod > 0);
                score += (100 * (T - t)) / T;
                // cout << ((100 * (T - t)) / T) << " " << t << " " << t/(double)T << " " << score << endl;
            }
            timeout:;
        }

        // cout << __func__ << ":" << __LINE__ << " " << score << endl;
        if (score > bestscore)
        {
            bestscore = score;
            cout << score << endl;
            writeOutput();
        }
    }
}

int main(int argc, char * argv[])
{
    seed = time(NULL) ^ getpid();
    srand(seed);

    assert(argc >= 3);
    outputdir = argv[2];
    readInput(argv[1]);

    // Visu::init(argc, argv, render, 0, X, 0, Y);

    solve();
    // Visu::display();
}
