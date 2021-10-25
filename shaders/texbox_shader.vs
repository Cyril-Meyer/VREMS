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
		//position.y = clamp(position.y, 0.0, max_height);
		vec3 position2 = vec3(position.x, clamp(position.y, 0.0, max_height), position.z);
		gl_Position =  projection * view * model * vec4(position2 - center , 1.0f);
		//float ratio = max_height / (position.y ? position.y : ; 
		//outTexCoord = vec2(inTexCoord.x, inTexCoord.y);
		outTexCoord = vec2(inTexCoord.x, inTexCoord.y * (position.y == 0.0 ? position.y : max_height / position.y));
	}