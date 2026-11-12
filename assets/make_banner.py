#!/usr/bin/env python
"""Render the README banner: the four textured reconstructions side by side on a black background (CPU only).

The meshes are RNb-NeuS2 reconstructions of the VISART paper, textured with the albedo maps (LED-getter normals and
albedo; for the Gourdan bone, whose paper method Uni-MS-PS estimates no albedo, the LED-getter alternative template).
They are not part of this repository: pass the folder holding one sub-folder per object, each with texturedMesh.obj,
texturedMesh.mtl and texture_*.png (sRGB), as written by the Meshroom Texturing node.

Rendering: points sampled on the surface, colored by the texture, Lambertian shading, z-buffer splatting.

Usage:
    python make_banner.py <meshes folder> [--out banner.png] [--height 640] [--samples 12000000]
    python make_banner.py <meshes folder> --preview <object>   # 6 axis views of one object, to choose a rotation
"""
import argparse
import os

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont

# object: (sub-folder, rotation applied after PCA alignment as (axis, degrees) steps, label, height in the banner)
OBJECTS = {
    "warrior": ("warrior_ledgetter", [("x", 90), ("z", -90), ("y", -25)], "Warrior", 1.0),
    "biface": ("biface_ledgetter_rig", [("z", -90)], "Biface", 1.0),
    "calathos": ("calathos_ledgetter_rig", [("z", 90), ("y", 15)], "Calathos", 1.0),
    # elongated (about 4.5:1): drawn lying, smaller
    "gourdan_bone": ("gourdan_bone_ledgetter_rig", [("x", -15)], "Gourdan bone", 0.4),
}
LIGHT = np.array([-0.4, 0.5, 0.75])


def rotation(axis, degrees):
    return trimesh.transformations.rotation_matrix(np.radians(degrees), np.eye(3)["xyz".index(axis)])[:3, :3]


def loadObject(folder):
    mesh = trimesh.load(os.path.join(folder, "texturedMesh.obj"), process=False, force="mesh")
    image = np.asarray(mesh.visual.material.image.convert("RGB"), dtype=np.float32) / 255.0
    vertices = mesh.vertices - mesh.vertices.mean(axis=0)
    # PCA frame: x = largest extent, y = middle, z = smallest (towards the viewer)
    _, _, axes = np.linalg.svd(vertices[:: max(1, len(vertices) // 200000)], full_matrices=False)
    if np.linalg.det(axes) < 0:
        axes[2] *= -1
    mesh.vertices = vertices @ axes.T
    return mesh, image


def samplePoints(mesh, image, count, rng):
    points, faces = trimesh.sample.sample_surface(mesh, count, seed=int(rng.integers(1 << 31)))
    triangles = mesh.vertices[mesh.faces[faces]]
    bary = trimesh.triangles.points_to_barycentric(triangles, points)
    uv = np.einsum("ij,ijk->ik", bary, mesh.visual.uv[mesh.faces[faces]])
    h, w = image.shape[:2]
    col = image[np.clip(((1 - uv[:, 1]) * h).astype(int), 0, h - 1), np.clip((uv[:, 0] * w).astype(int), 0, w - 1)]
    normals = np.einsum("ij,ijk->ik", bary, mesh.vertex_normals[mesh.faces[faces]])
    normals /= np.linalg.norm(normals, axis=1, keepdims=True) + 1e-12
    return points, normals, col


def render(points, normals, colors, rot, height, light=LIGHT):
    p = points @ rot.T
    n = normals @ rot.T
    # view along -z, image y up = +y
    xy = p[:, :2]
    lo, hi = xy.min(axis=0), xy.max(axis=0)
    scale = (height * 0.92) / (hi[1] - lo[1])
    width = int(np.ceil((hi[0] - lo[0]) * scale / 0.92)) + 1
    u = ((xy[:, 0] - (lo[0] + hi[0]) / 2) * scale + width / 2).astype(int)
    v = (height / 2 - (xy[:, 1] - (lo[1] + hi[1]) / 2) * scale).astype(int)
    ok = (u >= 0) & (u < width) & (v >= 0) & (v < height)
    u, v, z, n, c = u[ok], v[ok], p[ok, 2], n[ok], colors[ok]
    order = np.argsort(z)  # far first, near points overwrite
    img = np.zeros((height, width, 3), np.float32)
    mask = np.zeros((height, width), bool)
    l = light / np.linalg.norm(light)
    # albedo of arbitrary scale (LED-getter): bring the bright end to 1
    c = c / max(np.percentile(c.max(axis=1), 99.5), 1e-3)
    shade = 0.25 + 0.85 * np.clip(n @ l, 0, None)
    img[v[order], u[order]] = np.clip(c[order] * shade[order, None], 0, 1)
    mask[v[order], u[order]] = True
    return img, mask


def toSrgb(img):
    return np.where(img <= 0.0031308, 12.92 * img, 1.055 * np.power(img, 1 / 2.4) - 0.055)


def objectImage(folder, steps, height, samples, rng):
    mesh, image = loadObject(folder)
    rot = np.eye(3)
    for axis, deg in steps:
        rot = rotation(axis, deg) @ rot
    pts, nrm, col = samplePoints(mesh, image, samples, rng)
    img, mask = render(pts, nrm, col, rot, height)
    return img, mask


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("meshes")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "banner.png"))
    ap.add_argument("--height", type=int, default=640)
    ap.add_argument("--samples", type=int, default=12000000)
    ap.add_argument("--preview")
    args = ap.parse_args()
    rng = np.random.default_rng(0)

    if args.preview:
        sub = OBJECTS[args.preview][0]
        mesh, image = loadObject(os.path.join(args.meshes, sub))
        pts, nrm, col = samplePoints(mesh, image, args.samples, rng)
        views = [[], [("y", 180)], [("x", 90)], [("x", -90)], [("z", 90)], [("z", 90), ("y", 180)]]
        tiles = []
        for steps in views:
            rot = np.eye(3)
            for axis, deg in steps:
                rot = rotation(axis, deg) @ rot
            img, _ = render(pts, nrm, col, rot, args.height)
            tile = Image.fromarray((toSrgb(img) * 255).astype(np.uint8))
            ImageDraw.Draw(tile).text((8, 8), str(steps), fill=(255, 255, 0))
            tiles.append(tile)
        sheet = Image.new("RGB", (sum(t.width for t in tiles) + 10 * len(tiles), args.height), "black")
        x = 0
        for t in tiles:
            sheet.paste(t, (x, 0))
            x += t.width + 10
        sheet.save(args.out)
        print(args.out)
        return

    gap = args.height // 8
    labelH = args.height // 10
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", int(labelH * 0.55))
    except OSError:
        font = ImageFont.load_default()

    tiles = []
    for name, (sub, steps, label, size) in OBJECTS.items():
        img, _ = objectImage(os.path.join(args.meshes, sub), steps, int(args.height * size), args.samples, rng)
        print(name, img.shape)
        tiles.append((Image.fromarray((toSrgb(img) * 255).astype(np.uint8)), label))
    width = sum(t.width for t, _ in tiles) + gap * (len(tiles) + 1)
    banner = Image.new("RGB", (width, args.height + labelH), "black")
    draw = ImageDraw.Draw(banner)
    x = gap
    for t, label in tiles:
        banner.paste(t, (x, (args.height - t.height) // 2))
        tw = draw.textlength(label, font=font)
        draw.text((x + (t.width - tw) / 2, args.height + labelH * 0.1), label, fill=(190, 190, 190), font=font)
        x += t.width + gap
    banner.save(args.out, optimize=True)
    print(args.out, banner.size)

if __name__ == "__main__":
    main()
