#version 330

in vec2 outTexCoord;
uniform sampler2D samplerTex;
uniform float alpha;


void main(){
	vec4 tex = texture(samplerTex, outTexCoord);
	// gl_FragColor = vec4(1.0);
	gl_FragColor = vec4(tex.r, tex.r, tex.r, alpha);
}