#version 150

uniform sampler2D tex1;

in vec2 pos;
out vec4 FragColor;

void main(void)
{
    vec4 tex = texture(tex1, pos);
    FragColor = vec4(tex.r, tex.g, tex.b, 1);
}
