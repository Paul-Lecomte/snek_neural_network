import moderngl_window as mglw
import numpy as np
from pyrr import Matrix44
import moderngl

class Snake3DRenderer(mglw.WindowConfig):
    window_size = (800, 600)
    resource_dir = '.'
    aspect_ratio = 800 / 600
    title = "Snake 3D PPO"
    grid_size = (10, 10, 10)
    cell_size = 1.0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Données de la scène
        self.snake = [(5,5,5)]
        self.target = (2,2,2)
        self.obstacles = [(3,3,3), (7,7,7)]
        # OpenGL: activer depth test et créer la géométrie + shaders
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.cube_vbo = self.ctx.buffer(self._cube_vertices().astype('f4').tobytes())
        self.prog = self.ctx.program(
            vertex_shader=self._vertex_shader(),
            fragment_shader=self._fragment_shader()
        )
        self.cube_vao = self.ctx.simple_vertex_array(self.prog, self.cube_vbo, 'in_vert')
        # Matrices de caméra (vue + projection) construites manuellement
        self.proj = None
        self.view = None
        self._rebuild_camera()

    def _rebuild_camera(self):
        cx, cy, cz = self.grid_size[0]/2, self.grid_size[1]/2, self.grid_size[2]/2
        eye = (cx, -self.grid_size[1]*2, self.grid_size[2]*2)
        target = (cx, cy, cz)
        up = (0.0, 0.0, 1.0)
        width, height = self.wnd.buffer_size
        aspect = max(width / max(1, height), 1e-6)
        self.proj = Matrix44.perspective_projection(45.0, aspect, 0.1, 100.0)
        self.view = Matrix44.look_at(eye, target, up)

    def _cube_vertices(self):
        v = np.array([
            [-0.5,-0.5,-0.5], [ 0.5,-0.5,-0.5], [ 0.5, 0.5,-0.5], [-0.5, 0.5,-0.5],
            [-0.5,-0.5, 0.5], [ 0.5,-0.5, 0.5], [ 0.5, 0.5, 0.5], [-0.5, 0.5, 0.5],
        ], dtype=np.float32)
        idx = [0,1,2, 2,3,0, 1,5,6, 6,2,1, 5,4,7, 7,6,5, 4,0,3, 3,7,4, 3,2,6, 6,7,3, 4,5,1, 1,0,4]
        return v[idx]

    def _vertex_shader(self):
        return '''
        #version 330
        uniform mat4 mvp;
        in vec3 in_vert;
        void main() {
            gl_Position = mvp * vec4(in_vert, 1.0);
        }
        '''

    def _fragment_shader(self):
        return '''
        #version 330
        uniform vec3 color;
        out vec4 fragColor;
        void main() {
            fragColor = vec4(color, 1.0);
        }
        '''

    def on_resize(self, width: int, height: int):
        # Refaire la projection sur resize
        self._rebuild_camera()

    def on_render(self, time: float, frame_time: float):
        # S'assurer que le viewport et les matrices sont valides
        w, h = self.wnd.buffer_size
        self.ctx.viewport = (0, 0, int(w), int(h))
        if self.proj is None or self.view is None:
            self._rebuild_camera()
        self.ctx.clear(0.2, 0.2, 0.4, 1.0)
        # Dessiner le serpent
        for i, s in enumerate(self.snake):
            color = (0,1,0) if i == 0 else (0,0.7,0)
            self._draw_cube(s, color)
        # Dessiner la cible
        self._draw_cube(self.target, (1,0,0))
        # Dessiner les obstacles
        for o in self.obstacles:
            self._draw_cube(o, (0.4,0.4,0.4))

    def _draw_cube(self, pos, color):
        translate = Matrix44.from_translation([
            pos[0]*self.cell_size, pos[1]*self.cell_size, pos[2]*self.cell_size
        ])
        scale = Matrix44.from_scale([self.cell_size]*3)
        mvp = self.proj @ self.view @ translate @ scale
        self.prog['mvp'].write(mvp.astype('f4').tobytes())
        self.prog['color'].value = color
        self.cube_vao.render()

if __name__ == '__main__':
    mglw.run_window_config(Snake3DRenderer)
