#version 330

layout (points) in;
layout (triangle_strip, max_vertices = 24) out;

out float brightness;

const vec3 lightDir = -normalize(vec3(0.0, -0.5, -0.8));

uniform mat4 view;
uniform mat4 projection;
uniform mat4 model;
uniform vec4 label_color;
uniform float max_height;
uniform vec3 center;

const vec3 faceNormal0 = vec3(0.0, 0.0, 1.0);
const vec3 faceNormal1 = vec3(1.0, 0.0, 0.0);
const vec3 faceNormal2 = vec3(0.0, 0.0, -1.0);
const vec3 faceNormal3 = vec3(-1.0, 0.0, 0.0);
const vec3 faceNormal4 = vec3(0.0, 1.0, 0.0);
const vec3 faceNormal5 = vec3(0.0, -1.0, 0.0);

const vec4 vert0 = vec4(-1.0, 1.0, 1.0, 0.0);
const vec4 vert1 = vec4(-1.0, -1.0, 1.0, 0.0);
const vec4 vert2 = vec4(1.0, 1.0, 1.0, 0.0);
const vec4 vert3 = vec4(1.0, -1.0, 1.0, 0.0);
const vec4 vert4 = vec4(1.0, 1.0, -1.0, 0.0);
const vec4 vert5 = vec4(1.0, -1.0, -1.0, 0.0);
const vec4 vert6 = vec4(-1.0, 1.0, -1.0, 0.0);
const vec4 vert7 = vec4(-1.0, -1.0, -1.0, 0.0);

void createVertex(vec4 offset, vec3 faceNormal){
	vec4 worldPos = gl_in[0].gl_Position + offset;
	gl_Position = projection * view * model * worldPos;
	brightness = clamp(dot(lightDir, faceNormal), 0.1, 1.0);
	EmitVertex();
}

void main(void){
	if(gl_in[0].gl_Position.y <= (max_height - center.y)){
		mat4 invertModel = transpose(inverse(model));

		vec3 normal0 = normalize((invertModel * vec4(faceNormal0, 1.0)).xyz);
		createVertex(vert0, normal0);
		createVertex(vert1, normal0);
		createVertex(vert2, normal0);
		createVertex(vert3, normal0);
		EndPrimitive();

		vec3 normal1 = normalize((invertModel * vec4(faceNormal1, 1.0)).xyz);
		createVertex(vert2, normal1);
		createVertex(vert3, normal1);
		createVertex(vert4, normal1);
		createVertex(vert5, normal1);
		EndPrimitive();

		vec3 normal2 = normalize((invertModel * vec4(faceNormal2, 1.0)).xyz);
		createVertex(vert4, normal2);
		createVertex(vert5, normal2);
		createVertex(vert6, normal2);
		createVertex(vert7, normal2);
		EndPrimitive();

		vec3 normal3 = normalize((invertModel * vec4(faceNormal3, 1.0)).xyz);
		createVertex(vert6, normal3);
		createVertex(vert7, normal3);
		createVertex(vert0, normal3);
		createVertex(vert1, normal3);
		EndPrimitive();

		vec3 normal4 = normalize((invertModel * vec4(faceNormal4, 1.0)).xyz);
		createVertex(vert2, normal4);
		createVertex(vert4, normal4);
		createVertex(vert0, normal4);
		createVertex(vert6, normal4);
		EndPrimitive();

		vec3 normal5 = normalize((invertModel * vec4(faceNormal5, 1.0)).xyz);
		createVertex(vert1, normal5);
		createVertex(vert7, normal5);
		createVertex(vert3, normal5);
		createVertex(vert5, normal5);
		EndPrimitive();
	}
}