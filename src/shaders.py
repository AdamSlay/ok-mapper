# Contains all the shaders used in the program

# Grey Outline
VERTEX_OUTLINE_GREY = '''
            #version 330
            in vec2 in_vert;
            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
            }
        '''
FRAGMENT_OUTLINE_GREY = '''
            #version 330
            out vec4 color;
            void main() {
                color = vec4(0.6, 0.6, 0.6, 1.0);
            }
        '''

# Black Outline
VERTEX_OUTLINE_BLACK = '''
            #version 330
            in vec2 in_vert;
            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
            }
        '''
FRAGMENT_OUTLINE_BLACK = '''
            #version 330
            out vec4 color;
            void main() {
                color = vec4(0.0, 0.0, 0.0, 1.0);
            }
        '''

# Grey Fill
VERTEX_POINT_GREY = '''
        #version 330
        in vec2 in_vert;
        void main() {
            gl_Position = vec4(in_vert, 0.0, 1.0);
        }
    '''
FRAGMENT_POINT_GREY = '''
        #version 330
        out vec4 color;
        void main() {
            color = vec4(0.6, 0.6, 0.6, 1.0); // Gray color
        }
    '''