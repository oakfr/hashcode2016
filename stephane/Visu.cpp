// #include "Visu.h"
// #include <unistd.h>
// #include <cstdlib>
// #include <iostream>
// #include <vector>

// namespace Visu
// {

// using namespace std;

// void (*renderFunction)() = NULL;
// double xmin = 0;
// double xmax = 1.;
// double ymin = 0.;
// double ymax = 1.;
// struct KeyAction { int key; int action; };
// vector<KeyAction> keyActions;
// bool enabled = true;
// double delay = .1;
// bool pause = false;
// int step = 0.;
// int currentStep = 0.;

// int GLFWCALL windowClosedCallback()
// {
//   exit(1);
// }

// void GLFWCALL keyCallback(int key, int action)
// {
//   keyActions.push_back({key, action});
// }

// void init(int argc, char * argv[],
//           void (*renderFunction)(),
//           double xmin, double xmax, double ymin, double ymax)
// {
//   bool help = false;
//   int opt;
//   while ((opt = getopt(argc, argv, "hd:pvf:")) != -1)
//     switch (opt) {
//     case 'h': help = true; break;
//     case 'v': enabled = false; break;
//     case 'd': delay = atof(optarg); break;
//     case 'p': pause = true; break;
//     case 'f': step = atoi(optarg); break;
//     default:;
//     }

//   if (help) {
//     cerr << "-v          Desactive le visualiseur" << endl;
//     cerr << "-d [DELAY]  Delai entre deux frames, reel, en seconde" << endl;
//     cerr << "-p          Mettre en pause au lancement" << endl;
//     cerr << "-f [FRAME]  Aller directement a la frame numero [FRAME] " << endl;
//     cerr << "-h          Affiche l'aide" << endl;
//     cerr << endl;
//     cerr << "[escape] ou [q]    Stoppe le process" << endl;
//     cerr << "[right]            Frame suivante" << endl;
//     cerr << "[space]            (Des)active la pause" << endl;
//     cerr << "[f]                Affiche le numero de la frame" << endl;
//     cerr << endl;
//   }

//   if (enabled) {
//     glfwInit();

//     int width = 1600;
//     int height = 800;
//     glfwOpenWindow(width, height, 8,8,8,8,8,8, GLFW_WINDOW);
//     // glfwSetWindowPos(800, 0);
//     glfwSetWindowTitle("Criteo.SPOT");

//     glClearColor(1., 1., 1., 1.);

//     glfwSetWindowCloseCallback(windowClosedCallback);
//     glfwSetKeyCallback(keyCallback);
//     glfwSwapBuffers();

//     Visu::renderFunction = renderFunction;
//     Visu::xmin = xmin;
//     Visu::xmax = xmax;
//     Visu::ymin = ymin;
//     Visu::ymax = ymax;

//     glMatrixMode(GL_PROJECTION);
//     glLoadIdentity();

//     double dx = xmax-xmin;
//     double dy = ymax-ymin;
//     double ymargin = max((dx*width/height-dy)/2, 0.);
//     double xmargin = max((dy*height/width-dx)/2, 0.);

//     glOrtho(ymin-ymargin, ymax+ymargin, xmin-xmargin, xmax+xmargin, -1, 1);
//     glTranslatef(0., xmax, 0.);
//     glRotatef(-90, 0., 0., 1.);

//     glMatrixMode(GL_MODELVIEW);
//   }
// }

// void handleEvents()
// {
//   for (unsigned int i = 0; i < keyActions.size(); ++i) {
//     int key = keyActions[i].key;
//     int action = keyActions[i].action;

//     if (action == GLFW_PRESS) {
//       switch (key) {
//       case GLFW_KEY_ESC:
//       case 'Q':
//         exit(1);
//       case 'C':
//         if (glfwGetKey(GLFW_KEY_LCTRL) == GLFW_PRESS)
//           exit(1);
//       case 'F':
//         cerr << "frame courante = " << currentStep << endl;
//         break;
//       case GLFW_KEY_RIGHT:
//         step = currentStep + 1;
//         break;
//       case GLFW_KEY_SPACE:
//         pause = !pause;
//         break;
//       default:;
//       }
//     }
//   }
//   keyActions.clear();
// }

// void display()
// {
//   if (enabled) {
//     if (currentStep < step) {
//       ++currentStep;
//       return;
//     }
//     glLoadIdentity();
//     glClear(GL_COLOR_BUFFER_BIT);
//     (*renderFunction)();
//     glfwSwapBuffers();
//     handleEvents();
//     bool currentPause = pause;
//     int iter = 200. * delay;
//     for (int i = 0; (i < iter || currentPause) && currentStep >= step; ++i) {
//       usleep(5000);
//       glLoadIdentity();
//       glClear(GL_COLOR_BUFFER_BIT);
//       (*renderFunction)();
//       glfwSwapBuffers();
//       handleEvents();
//       currentPause = pause;
//     }
//     ++currentStep;
//   }
// }

// }
