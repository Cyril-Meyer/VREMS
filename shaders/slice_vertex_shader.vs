	#version 330
	
	in vec3 position;
	in vec2 inTexCoord;

	uniform mat4 view;
	uniform mat4 projection;
	uniform mat4 model;
	uniform float max_height;
	uniform vec3 center;

	out vec2 outTexCoord;

	void main(){
		gl_Position =  projection * view * model * vec4(position - center + vec3(0.0, max_height, 0.0), 1.0f);
		outTexCoord = inTexCoord;
	}