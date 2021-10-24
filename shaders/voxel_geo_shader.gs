#version 330

layout (points) in;
layout (triangle_strip, max_vertices = 24) out;

out float brightness;

const vec3 lightDir = normalize(vec3(0.0, -0.5, -0.8));

uniform mat4 view;
uniform mat4 projection;
uniform mat4 model;
uniform vec4 label_color;
uniform float size_voxel;
uniform float max_height;
uniform vec3 center;

const vec3 faceNormal0 = vec3(0.0, 0.0, 1.0);
const vec3 vert0_0 = vec3(-1.0, 1.0, 1.0);
const vec3 vert0_1 = vec3(-1.0, -1.0, 1.0);
const vec3 vert0_2 = vec3(1.0, 1.0, 1.0);
const vec3 vert0_3 = vec3(1.0, -1.0, 1.0);

const vec3 faceNormal1 = vec3(1.0, 0.0, 0.0);
const vec3 vert1_0 = vec3(1.0, 1.0, 1.0);
const vec3 vert1_1 = vec3(1.0, -1.0, 1.0);
const vec3 vert1_2 = vec3(1.0, 1.0, -1.0);
const vec3 vert1_3 = vec3(1.0, -1.0, -1.0);

const vec3 faceNormal2 = vec3(0.0, 0.0, -1.0);
const vec3 vert2_0 = vec3(1.0, 1.0, -1.0);
const vec3 vert2_1 = vec3(1.0, -1.0, -1.0);
const vec3 vert2_2 = vec3(-1.0, 1.0, -1.0);
const vec3 vert2_3 = vec3(-1.0, -1.0, -1.0);

const vec3 faceNormal3 = vec3(-1.0, 0.0, 0.0);
const vec3 vert3_0 = vec3(-1.0, 1.0, -1.0);
const vec3 vert3_1 = vec3(-1.0, -1.0, -1.0);
const vec3 vert3_2 = vec3(-1.0, 1.0, 1.0);
const vec3 vert3_3 = vec3(-1.0, -1.0, 1.0);

const vec3 faceNormal4 = vec3(0.0, 1.0, 0.0);
const vec3 vert4_0 = vec3(1.0, 1.0, 1.0);
const vec3 vert4_1 = vec3(1.0, 1.0, -1.0);
const vec3 vert4_2 = vec3(-1.0, 1.0, 1.0);
const vec3 vert4_3 = vec3(-1.0, 1.0, -1.0);

const vec3 faceNormal5 = vec3(0.0, -1.0, 0.0);
const vec3 vert5_0 = vec3(-1.0, -1.0, 1.0);
const vec3 vert5_1 = vec3(-1.0, -1.0, -1.0);
const vec3 vert5_2 = vec3(1.0, -1.0, 1.0);
const vec3 vert5_3 = vec3(1.0, -1.0, -1.0);

const vec4 zero = vec4(0.0);

void createVertex(vec3 offset, vec3 faceNormal){
	vec4 offset4 = vec4(offset * size_voxel, 0.0);
	vec4 worldPos = gl_in[0].gl_Position + offset4;
	gl_Position = projection * view * model * worldPos;
	vec3 faceNormal2 = (model * vec4(faceNormal, 1.0)).xyz;
	brightness = max(dot(-lightDir, faceNormal2), 0.1);
	EmitVertex();
}

void main(void){
	if(gl_in[0].gl_Position.y <= (max_height - center.y)){
		createVertex(vert0_0, faceNormal0);
		createVertex(vert0_1, faceNormal0);
		createVertex(vert0_2, faceNormal0);
		createVertex(vert0_3, faceNormal0);
		EndPrimitive();

		createVertex(vert1_0,faceNormal1);
		createVertex(vert1_1,faceNormal1);
		createVertex(vert1_2,faceNormal1);
		createVertex(vert1_3,faceNormal1);
		EndPrimitive();
		
		createVertex(vert2_0,faceNormal2);
		createVertex(vert2_1,faceNormal2);
		createVertex(vert2_2,faceNormal2);
		createVertex(vert2_3,faceNormal2);
		EndPrimitive();

		createVertex(vert3_0,faceNormal3);
		createVertex(vert3_1,faceNormal3);
		createVertex(vert3_2,faceNormal3);
		createVertex(vert3_3,faceNormal3);
		EndPrimitive();

		createVertex(vert4_0,faceNormal4);
		createVertex(vert4_1,faceNormal4);
		createVertex(vert4_2,faceNormal4);
		createVertex(vert4_3,faceNormal4);
		EndPrimitive();

		createVertex(vert5_0,faceNormal5 );
		createVertex(vert5_1,faceNormal5 );
		createVertex(vert5_2,faceNormal5 );
		createVertex(vert5_3,faceNormal5 );
		EndPrimitive();
	}
}