	#version 330

	in float brightness;
	uniform vec4 label_color;

	void main(){
		
	gl_FragColor = vec4(label_color.xyz * brightness, label_color.w);
}