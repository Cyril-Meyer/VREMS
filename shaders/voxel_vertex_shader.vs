	#version 330
	in vec3 position;

	uniform mat4 view;
	uniform mat4 projection;
	uniform mat4 model;
	uniform vec4 label_color;
	uniform vec3 center;

	void main(){
		gl_Position = vec4(position - center, 1.0f);
	}