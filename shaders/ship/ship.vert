#version 330

in vec3 vPosition;
uniform mat4 transformation;

void main() {
    gl_Position = vec4(vPosition, 1.0) * transformation;
}