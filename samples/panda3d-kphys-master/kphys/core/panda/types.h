#ifndef PANDA_TYPES_H
#define PANDA_TYPES_H

#include "nodePath.h"

#define MAX_BONES 256
#define FLOAT_SIZE 4
#define MAT4_SIZE (MAT4_WIDTH * MAT4_HEIGHT * FLOAT_SIZE)
#define MAT4_WIDTH 4
#define MAT4_HEIGHT 4
#define RGBA_CHANNEL_COUNT 4
#define RGBA_MAT4_SIZE ((MAT4_WIDTH * MAT4_HEIGHT) / RGBA_CHANNEL_COUNT)


typedef union LMatrix4Array {
    LMatrix4 matrices[MAX_BONES];
    unsigned char data[MAT4_SIZE * MAX_BONES];
} LMatrix4Array;

LMatrix4 get_matrix(LMatrix4Array* array, unsigned short i);
void set_matrix(LMatrix4Array* array, unsigned short i, LMatrix4 matrix);
int is_armature(NodePath np);
int is_bone(NodePath np);
int is_effector(NodePath np);
NodePath get_armature(NodePath np);

#endif
