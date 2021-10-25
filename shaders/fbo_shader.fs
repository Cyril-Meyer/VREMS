	#version 330

	in vec2 outTexCoord;
	uniform sampler2D samplerTex;

	void main(){
        gl_FragColor = vec4(texture(samplerTex, outTexCoord).xyz, 1.0);
	}
