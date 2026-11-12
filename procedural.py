# Math functions to generate the case, spinning disc, and rose flower
import numpy as np
from .config import (
    CASE_SIZE, CORNER_RADIUS, WALL_THICKNESS, INNER_TRAY_RADIUS,
    LATCH_LEFT, LATCH_RIGHT, LATCH_BOTTOM, LATCH_TOP,
    DISC_RADIUS, HOLE_RADIUS, CLAMP_RADIUS, PIN_DISTANCE, PIN_RADIUS, STEP_RADIUS,
    GROOVE_START, GROOVE_END,
    BG_COLOR, CASE_RIM_COLOR, DISC_EDGE_COLOR, DISC_SURFACE_COLOR,
    ROSE_RED, ROSE_DARK, ROSE_LIGHT,
    ROT_SPEED
)


def box_dist(x, y, w, h, r):
    # Calculates distance to a rounded rectangle edge
    dx = np.maximum(np.abs(x) - (w - r), 0.0)
    dy = np.maximum(np.abs(y) - (h - r), 0.0)
    outside = np.sqrt(dx * dx + dy * dy)
    inside = np.minimum(np.maximum(np.abs(x) - (w - r), np.abs(y) - (h - r)), 0.0)
    return outside + inside - r


def smooth_step(edge0, edge1, x):
    # Smooth transition between edge0 and edge1
    t = np.clip((x - edge0) / (edge1 - edge0 + 1e-9), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def draw_rose(r, theta_rot):
    # Generates the rose petals using layered polar math
    # Each layer has: base_radius, wave_height, petal_count, angle_shift, second_wave
    layers = [
        (0.53, 0.065, 5.0, 0.35, 0.025),   # Layer 5: large outer petals
        (0.44, 0.055, 5.0, 1.60, 0.020),   # Layer 4: middle petals
        (0.35, 0.045, 6.0, 0.80, 0.018),   # Layer 3: inner-middle petals
        (0.27, 0.038, 5.0, 2.10, 0.015),   # Layer 2: smaller petals
        (0.20, 0.028, 4.0, 1.10, 0.012),   # Layer 1: bud petals
        (0.14, 0.020, 3.0, 0.40, 0.008),   # Layer 0: center core
    ]

    rose_mask = np.zeros_like(r, dtype=np.float32)
    height_map = np.zeros_like(r, dtype=np.float32)
    crease_shadow = np.zeros_like(r, dtype=np.float32)

    # Draw from center outward so outer petals sit on top
    for idx, (base_r, amp, num_petals, angle_shift, sec_amp) in enumerate(reversed(layers)):
        layer_num = len(layers) - 1 - idx
        # Calculate curvy shape of the petal edge
        curve = base_r + amp * np.cos(num_petals * theta_rot + angle_shift) \
                + sec_amp * np.sin(2.0 * num_petals * theta_rot)

        dist_to_edge = r - curve
        petal_width = 0.08 + 0.02 * layer_num
        inside = smooth_step(0.015, -0.015, dist_to_edge)

        # Petal curved surface height
        u = np.clip((curve - r) / petal_width, 0.0, 1.0)
        h = np.sin(u * np.pi * 0.5) ** 1.3

        # Dark lines where petals overlap
        shadow = np.exp(-((dist_to_edge) / 0.018) ** 2)

        height_map = np.maximum(height_map, h * (0.3 + 0.12 * layer_num) * inside)
        crease_shadow = np.maximum(crease_shadow, shadow * inside)
        rose_mask = np.maximum(rose_mask, inside)

    # Cut out the center hole so the disc spindle shows through
    hole_mask = smooth_step(HOLE_RADIUS - 0.005, HOLE_RADIUS + 0.015, r)
    rose_mask *= hole_mask
    height_map *= hole_mask
    crease_shadow *= hole_mask

    # Subtle radial lines for petal texture
    vein_lines = 0.06 * np.sin(52.0 * theta_rot) * smooth_step(0.14, 0.50, r)

    return rose_mask, height_map, crease_shadow, vein_lines


def draw_case(x, y):
    # Calculates the plastic case borders, rounded corners, and left latch
    # Outer square box with rounded corners
    outer_dist = box_dist(x, y, CASE_SIZE, CASE_SIZE, CORNER_RADIUS)
    
    # Inner wall of the border
    inner_wall_dist = box_dist(x, y, CASE_SIZE - WALL_THICKNESS, 
                               CASE_SIZE - WALL_THICKNESS, 
                               CORNER_RADIUS * 0.7)

    case_mask = (outer_dist <= 0.01)

    # Shiny light reflections on the plastic edges
    edge_shine = np.exp(-((outer_dist) / 0.009) ** 2) * 1.5
    inner_shine = np.exp(-((inner_wall_dist) / 0.008) ** 2) * 0.9

    # Extra brightness at corners
    corners = (np.abs(x) > 0.70) & (np.abs(y) > 0.70)
    corner_shine = np.exp(-((outer_dist) / 0.020) ** 2) * corners * 0.8

    # Left latch tab
    latch_tab = box_dist(x - (LATCH_LEFT + 0.05), y, 0.06, 0.14, 0.03)
    latch_shine = np.exp(-((latch_tab) / 0.008) ** 2) * 1.2
    
    # Small cutouts on top and bottom of the latch
    notch_top = (x >= LATCH_LEFT) & (x <= LATCH_RIGHT) & (np.abs(y - 0.17) < 0.028)
    notch_bot = (x >= LATCH_LEFT) & (x <= LATCH_RIGHT) & (np.abs(y + 0.17) < 0.028)
    notch_shine = (notch_top | notch_bot) * 0.8

    # Circular line where the CD sits in the tray
    radius_from_center = np.sqrt(x * x + y * y)
    tray_line = np.exp(-((radius_from_center - INNER_TRAY_RADIUS) / 0.007) ** 2) * 0.75

    # Total light reflection on the case
    case_highlights = edge_shine + inner_shine + corner_shine + \
                      latch_shine + notch_shine + tray_line

    # Soft light glow just outside the box
    case_glow = np.exp(-((np.maximum(outer_dist, 0.0)) / 0.045) ** 2) * 0.35

    return case_mask, case_highlights, case_glow


def draw_disc(r, theta, theta_rot):
    # Calculates the CD disc lines, clamp ring, 4 holes, and light sheen
    disc_mask = (r <= DISC_RADIUS) & (r >= HOLE_RADIUS)
    disc_rim = np.exp(-((r - DISC_RADIUS) / 0.007) ** 2) * 1.4

    # Center open hole
    is_in_hole = r < HOLE_RADIUS

    # Center plastic clamp area
    clamp_rim = np.exp(-((r - CLAMP_RADIUS) / 0.006) ** 2) * 0.95

    # 4 small pin holes in the clamp ring that rotate with the disc
    pin_angles = np.array([0.0, 0.5 * np.pi, np.pi, 1.5 * np.pi], dtype=np.float32)
    pin_distances = []
    for angle in pin_angles:
        d_ang = np.abs((theta_rot - angle + np.pi) % (2.0 * np.pi) - np.pi)
        d = np.sqrt(r * r + PIN_DISTANCE * PIN_DISTANCE - 2.0 * r * PIN_DISTANCE * np.cos(d_ang))
        pin_distances.append(d)
    closest_pin_dist = np.minimum.reduce(pin_distances)
    
    is_in_pin = (closest_pin_dist < PIN_RADIUS)
    pin_rim = np.exp(-((closest_pin_dist - PIN_RADIUS) / 0.004) ** 2) * 1.1

    # Inner step ridge
    step_rim = np.exp(-((r - STEP_RADIUS) / 0.006) ** 2) * 0.85

    # Concentric rings like CD data tracks
    is_data_area = (r >= GROOVE_START) & (r <= GROOVE_END)
    groove_texture = (0.5 + 0.5 * np.sin(180.0 * r)) * is_data_area * 0.25

    # Two-sided light reflection across the disc
    reflection1 = np.cos(theta - 0.785) ** 10
    reflection2 = np.cos(theta - 0.785 - np.pi) ** 10
    disc_sheen = (reflection1 + reflection2) * smooth_step(CLAMP_RADIUS, DISC_RADIUS, r) * 0.65

    # Slight moving flare that turns with the disc
    moving_flare = np.cos(theta_rot * 2.0) ** 14 * 0.35 * is_data_area

    disc_highlights = disc_rim + clamp_rim + pin_rim + \
                      step_rim + groove_texture + disc_sheen + moving_flare

    return disc_mask, is_in_hole, is_in_pin, disc_highlights


def draw_scene(x, y, t):
    # Renders one complete frame at time t
    r = np.sqrt(x * x + y * y)
    theta = np.arctan2(y, x)

    # Current rotation angle of the disc and rose
    rot_angle = ROT_SPEED * t
    theta_rot = (theta - rot_angle) % (2.0 * np.pi)

    # 1. Calculate each element
    case_mask, case_highlights, case_glow = draw_case(x, y)
    disc_mask, is_in_hole, is_in_pin, disc_highlights = draw_disc(r, theta, theta_rot)
    rose_mask, rose_height, rose_crease, rose_veins = draw_rose(r, theta_rot)

    # 2. Dark background
    frame = np.zeros((*x.shape, 3), dtype=np.float32)
    frame[:] = BG_COLOR

    # Add soft glow around the case
    frame += CASE_RIM_COLOR * case_glow[..., None]

    # 3. Add the clear plastic disc
    disc_visible = disc_mask & (~is_in_hole)
    frame = np.where(disc_visible[..., None], DISC_SURFACE_COLOR * 1.2, frame)
    frame = np.where(disc_visible[..., None], frame + (DISC_EDGE_COLOR * (disc_highlights[..., None] * 0.85)), frame)

    # 4. Add the red rose on the disc
    # Light coming from top-left
    lx, ly, lz = -0.38, -0.42, 0.82
    gx, gy = np.gradient(rose_height)
    nx = -gx * 3.5
    ny = -gy * 3.5
    nz = np.ones_like(nx)
    norm = np.sqrt(nx * nx + ny * ny + nz * nz + 1e-9)
    nx /= norm
    ny /= norm
    nz /= norm

    diffuse = np.clip(nx * lx + ny * ly + nz * lz, 0.0, 1.0)
    rim_light = (1.0 - nz) ** 2.2 * 1.3

    # Color the petals
    color = ROSE_RED * (diffuse[..., None] * 0.85 + 0.35)
    color += ROSE_LIGHT * rim_light[..., None]
    color += ROSE_LIGHT * (rose_veins[..., None] * 0.4)
    color = color * (1.0 - rose_crease[..., None] * 0.75)
    center_shadow = smooth_step(0.12, 0.22, r)[..., None]
    color = color * (0.6 + 0.4 * center_shadow)

    # Blend rose over disc
    frame = np.where((rose_mask[..., None] > 0.02) & disc_visible[..., None],
                     frame * (1.0 - rose_mask[..., None]) + color * rose_mask[..., None],
                     frame)

    # 5. Add small holes in the clamp ring
    frame = np.where(is_in_pin[..., None] & disc_visible[..., None],
                     ROSE_DARK * 0.35,
                     frame)

    # Center hole is open (shows dark background)
    frame = np.where(is_in_hole[..., None], BG_COLOR, frame)

    # 6. Add the outer case highlights on top
    frame += CASE_RIM_COLOR * (case_highlights[..., None] * 1.1)

    # Make colors look natural and clip
    frame = np.clip(frame, 0.0, None)
    frame = 1.0 - np.exp(-1.8 * frame)

    return frame
