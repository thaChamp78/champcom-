"""
ChampCom Render Pipeline - GPU-ready abstraction layer
This defines the INTERFACE that maps to real graphics APIs.
Implementations can target: Vulkan, OpenGL, Metal, or software.

This is the bridge between ChampCom and actual GPU rendering.
When you're ready to plug in Vulkan, you implement these interfaces.
"""
import time
from enum import Enum, auto


class ShaderStage(Enum):
    VERTEX = auto()
    FRAGMENT = auto()
    COMPUTE = auto()
    GEOMETRY = auto()


class BufferUsage(Enum):
    VERTEX = auto()
    INDEX = auto()
    UNIFORM = auto()
    STORAGE = auto()


class TextureFormat(Enum):
    RGBA8 = auto()
    RGB8 = auto()
    DEPTH32 = auto()
    DEPTH24_STENCIL8 = auto()


class Shader:
    """Represents a compiled shader program."""
    def __init__(self, name, stage, source):
        self.name = name
        self.stage = stage
        self.source = source
        self.compiled = False
        self.handle = None  # GPU handle set by backend

    def __repr__(self):
        return f"Shader({self.name}, {self.stage.name})"


class Buffer:
    """GPU buffer (vertex, index, uniform)."""
    def __init__(self, name, usage, size_bytes):
        self.name = name
        self.usage = usage
        self.size = size_bytes
        self.handle = None
        self.data = None

    def upload(self, data):
        self.data = data
        self.size = len(data) if isinstance(data, (bytes, bytearray)) else 0


class Texture:
    """GPU texture."""
    def __init__(self, name, width, height, fmt=TextureFormat.RGBA8):
        self.name = name
        self.width = width
        self.height = height
        self.format = fmt
        self.handle = None
        self.data = None


class RenderTarget:
    """Framebuffer / render target."""
    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height
        self.color_texture = Texture(f"{name}_color", width, height)
        self.depth_texture = Texture(f"{name}_depth", width, height,
                                      TextureFormat.DEPTH32)


class Material:
    """Shader + uniforms + textures = material."""
    def __init__(self, name, vertex_shader, fragment_shader):
        self.name = name
        self.vertex_shader = vertex_shader
        self.fragment_shader = fragment_shader
        self.uniforms = {}
        self.textures = {}

    def set_uniform(self, name, value):
        self.uniforms[name] = value

    def set_texture(self, slot, texture):
        self.textures[slot] = texture


class Mesh:
    """Vertex + index data."""
    def __init__(self, name):
        self.name = name
        self.vertex_buffer = None
        self.index_buffer = None
        self.vertex_count = 0
        self.index_count = 0


class DrawCommand:
    """A single draw call."""
    def __init__(self, mesh, material, transform=None):
        self.mesh = mesh
        self.material = material
        self.transform = transform or [
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1,
        ]  # Identity matrix (4x4 column-major)


class RenderPass:
    """A single pass in the render pipeline."""
    def __init__(self, name, target=None):
        self.name = name
        self.target = target  # None = screen
        self.draw_commands = []
        self.clear_color = (0.0, 0.0, 0.0, 1.0)
        self.clear_depth = True
        self.enabled = True

    def draw(self, mesh, material, transform=None):
        self.draw_commands.append(DrawCommand(mesh, material, transform))

    def clear(self):
        self.draw_commands.clear()


class RenderPipeline:
    """
    The main render pipeline. This is the abstraction that backends implement.

    Usage:
        pipeline = RenderPipeline()
        pipeline.set_backend(VulkanBackend())  # or OpenGLBackend, SoftwareBackend
        pipeline.add_pass(geometry_pass)
        pipeline.add_pass(lighting_pass)
        pipeline.add_pass(ui_pass)
        pipeline.execute()  # Runs all passes through the backend
    """

    def __init__(self):
        self.passes = []
        self.backend = None  # Set to a real GPU backend
        self.shaders = {}
        self.buffers = {}
        self.textures = {}
        self.materials = {}
        self.meshes = {}
        self.frame_count = 0
        self.frame_time = 0

    def set_backend(self, backend):
        """Set the GPU backend (Vulkan, OpenGL, etc)."""
        self.backend = backend

    def create_shader(self, name, stage, source):
        shader = Shader(name, stage, source)
        self.shaders[name] = shader
        if self.backend:
            self.backend.compile_shader(shader)
        return shader

    def create_buffer(self, name, usage, size):
        buf = Buffer(name, usage, size)
        self.buffers[name] = buf
        if self.backend:
            self.backend.create_buffer(buf)
        return buf

    def create_texture(self, name, width, height, fmt=TextureFormat.RGBA8):
        tex = Texture(name, width, height, fmt)
        self.textures[name] = tex
        if self.backend:
            self.backend.create_texture(tex)
        return tex

    def create_material(self, name, vert_name, frag_name):
        vs = self.shaders.get(vert_name)
        fs = self.shaders.get(frag_name)
        mat = Material(name, vs, fs)
        self.materials[name] = mat
        return mat

    def create_mesh(self, name):
        mesh = Mesh(name)
        self.meshes[name] = mesh
        return mesh

    def add_pass(self, render_pass):
        self.passes.append(render_pass)

    def remove_pass(self, name):
        self.passes = [p for p in self.passes if p.name != name]

    def execute(self):
        """Execute all render passes."""
        start = time.perf_counter()

        if self.backend:
            self.backend.begin_frame()
            for p in self.passes:
                if p.enabled:
                    self.backend.execute_pass(p)
            self.backend.end_frame()
        else:
            # Software fallback - just track stats
            for p in self.passes:
                if p.enabled:
                    p.clear()

        self.frame_time = time.perf_counter() - start
        self.frame_count += 1

    def get_stats(self):
        total_draws = sum(len(p.draw_commands) for p in self.passes)
        return {
            "frame_count": self.frame_count,
            "frame_time_ms": round(self.frame_time * 1000, 2),
            "passes": len(self.passes),
            "total_draw_commands": total_draws,
            "shaders": len(self.shaders),
            "buffers": len(self.buffers),
            "textures": len(self.textures),
            "materials": len(self.materials),
            "meshes": len(self.meshes),
            "backend": type(self.backend).__name__ if self.backend else "None (software)",
        }


class GPUBackend:
    """
    Abstract GPU backend interface.
    Implement this for Vulkan, OpenGL, Metal, or DirectX.

    To add Vulkan:
      1. Create VulkanBackend(GPUBackend) in render/vulkan_backend.py
      2. Implement each method with real vk* calls
      3. pipeline.set_backend(VulkanBackend())
    """

    def init(self, window_handle):
        raise NotImplementedError

    def compile_shader(self, shader):
        raise NotImplementedError

    def create_buffer(self, buffer):
        raise NotImplementedError

    def create_texture(self, texture):
        raise NotImplementedError

    def begin_frame(self):
        raise NotImplementedError

    def execute_pass(self, render_pass):
        raise NotImplementedError

    def end_frame(self):
        raise NotImplementedError

    def shutdown(self):
        raise NotImplementedError


# ============================================================
# Example shaders (GLSL) - ready for when a backend is plugged in
# ============================================================

BASIC_VERTEX_SHADER = """
#version 450

layout(location = 0) in vec3 inPosition;
layout(location = 1) in vec3 inNormal;
layout(location = 2) in vec2 inTexCoord;

layout(binding = 0) uniform MVP {
    mat4 model;
    mat4 view;
    mat4 projection;
} mvp;

layout(location = 0) out vec3 fragNormal;
layout(location = 1) out vec2 fragTexCoord;

void main() {
    gl_Position = mvp.projection * mvp.view * mvp.model * vec4(inPosition, 1.0);
    fragNormal = mat3(mvp.model) * inNormal;
    fragTexCoord = inTexCoord;
}
"""

BASIC_FRAGMENT_SHADER = """
#version 450

layout(location = 0) in vec3 fragNormal;
layout(location = 1) in vec2 fragTexCoord;

layout(location = 0) out vec4 outColor;

layout(binding = 1) uniform sampler2D texSampler;

void main() {
    vec3 lightDir = normalize(vec3(1.0, 1.0, 1.0));
    float diffuse = max(dot(normalize(fragNormal), lightDir), 0.2);
    vec4 texColor = texture(texSampler, fragTexCoord);
    outColor = vec4(texColor.rgb * diffuse, texColor.a);
}
"""
