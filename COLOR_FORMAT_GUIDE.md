# AirSim Color Format Guide: RGB vs BGR Video Processing

## Overview

This guide explains the critical color format differences between AirSim, OpenCV, and machine learning frameworks, and how to properly handle video creation for different use cases.

## The Problem: Color Space Confusion

### Root Cause
- **AirSim returns RGB data** (Red, Green, Blue)
- **OpenCV expects BGR data** (Blue, Green, Red) 
- **ML frameworks expect RGB data** (detectnet, YOLO, etc.)
- **Video codecs can be either** depending on implementation

### Symptoms
- ✗ Colors appear inverted (red objects look blue)
- ✗ Videos look unrealistic compared to AirSim simulator
- ✗ ML models perform poorly due to wrong color channels
- ✗ Inconsistent results between display and inference

## Color Format Matrix

| Source/Target | Format | Notes |
|---------------|--------|-------|
| AirSim `simGetImages()` | **RGB** | Native format from simulator |
| OpenCV `cv2.imread()` | **BGR** | Reads images as BGR by default |
| OpenCV `cv2.VideoWriter()` | **BGR** | Expects BGR input frames |
| imageio `imread()` | **RGB** | Preserves original RGB format |
| imageio `VideoWriter()` | **RGB** | Maintains RGB throughout |
| detectnet/YOLO | **RGB** | Standard ML format |
| Media players | **Either** | Handle both, but display may vary |

## Solutions Implemented

### 1. Image Capture & Storage

**File:** `controllers/base_controller.py`

```python
# ✓ CORRECT: Save raw RGB data from AirSim
def save_sensor_data(self, sensor_data):
    if sensor_data["rgb"] is not None:
        # Save raw RGB data directly (no BGR conversion)
        # This preserves RGB format for detectnet and ML applications
        compression_params = [cv2.IMWRITE_PNG_COMPRESSION, 1]
        cv2.imwrite(
            os.path.join(self.rgb_dir, f"rgb_{timestep:06d}.png"),
            sensor_data["rgb"],  # Raw RGB from AirSim
            compression_params
        )

# ✗ WRONG: Converting RGB to BGR
rgb_bgr = cv2.cvtColor(sensor_data["rgb"], cv2.COLOR_RGB2BGR)
cv2.imwrite(filename, rgb_bgr)  # Saves BGR data
```

### 2. Video Creation for Different Use Cases

**File:** `utils/data_visualizer.py`

#### For Machine Learning (RGB-native):
```python
def create_rgb_video_from_images(self, drone_name, image_type='rgb', fps=30):
    """Create RGB video for detectnet/ML applications."""
    import imageio
    
    # Use imageio for RGB-native video creation
    with imageio.get_writer(output_path, fps=fps, codec='libx264', quality=8) as writer:
        for image_name in images:
            # Read image preserving RGB format
            frame = imageio.imread(image_path)  # RGB format
            writer.append_data(frame)  # Write RGB directly
```

#### For Display (BGR conversion):
```python
def create_video_from_images(self, drone_name, image_type='rgb', fps=30):
    """Create BGR video for display/viewing."""
    # OpenCV video writer expects BGR
    for image_name in images:
        frame = cv2.imread(image_path)  # Reads as BGR
        video_writer.write(frame)  # BGR format
```

## Usage Guidelines

### Choose the Right Video Format

| Use Case | Video Type | Command | Output Format |
|----------|------------|---------|---------------|
| **Machine Learning** (detectnet, YOLO) | RGB | Option 5 | `*_video_rgb.mp4` |
| **Display/Viewing** | BGR | Option 3/4 | `*_video.avi` |
| **Both Applications** | Both | Option 6 | Both files |

### Visualization Script Options

```bash
./visualize.sh

# Options:
# 5. Create RGB video (for detectnet/ML)    ← Use for ML inference
# 6. Create both RGB and BGR videos         ← Best of both worlds
```

## Technical Details

### AirSim Image Request
```python
# AirSim returns RGB data
responses = client.simGetImages([
    airsim.ImageRequest("rgb_front", airsim.ImageType.Scene, False, True)
], vehicle_name=drone_name)

# Result: RGB uint8 array [Height, Width, 3] where channels are [R, G, B]
```

### Color Space Conversion Rules

```python
# ✓ CORRECT: RGB → BGR for OpenCV display
bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)

# ✓ CORRECT: BGR → RGB for ML processing  
rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

# ✗ WRONG: Double conversion
rgb_image = cv2.cvtColor(cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2RGB)
```

## Debugging Color Issues

### 1. Pixel Value Analysis
```python
# Check pixel values to identify format
import cv2
import imageio

# Method 1: OpenCV (reads as BGR)
bgr_img = cv2.imread('image.png')
print(f"OpenCV (BGR): {bgr_img[0, 0, :]}")  # [B, G, R]

# Method 2: imageio (reads as RGB)  
rgb_img = imageio.imread('image.png')
print(f"imageio (RGB): {rgb_img[0, 0, :]}")  # [R, G, B]
```

### 2. Visual Inspection
- **Sky should be blue** (high B in BGR, high R in RGB)
- **Grass should be green** (high G in both)
- **Red objects should look red** (high R in RGB, high B if wrongly interpreted)

### 3. Test with Known Colors
```python
# Create test image with known red pixel
test_img = np.zeros((100, 100, 3), dtype=np.uint8)
test_img[50, 50, :] = [255, 0, 0]  # Red pixel in RGB

# Save and read back to test pipeline
imageio.imwrite('test_rgb.png', test_img)
loaded = imageio.imread('test_rgb.png')
print(f"Red pixel preserved: {loaded[50, 50, :] == [255, 0, 0]}")
```

## Dependencies

### Required Packages
```bash
pip install imageio[ffmpeg] imageio-ffmpeg opencv-python numpy
```

### System Requirements
```bash
sudo apt update
sudo apt install ffmpeg libavcodec-extra
```

## File Naming Convention

- `{drone_name}_rgb_video_rgb.mp4` - RGB format for ML/detectnet
- `{drone_name}_rgb_video.avi` - BGR format for display
- `{drone_name}_ir_video_rgb.mp4` - RGB infrared video
- `{drone_name}_ir_video.avi` - BGR infrared video

## Best Practices

### ✅ DO:
- Use imageio for RGB-native video creation
- Keep separate pipelines for ML vs display
- Test with known color patterns
- Document your color format assumptions
- Use descriptive filenames indicating format

### ❌ DON'T:
- Mix OpenCV and imageio without understanding format differences
- Assume all video libraries handle colors the same way
- Convert colors unnecessarily (avoid double conversions)
- Use the same video for both display and ML without verification

## Common Pitfalls

1. **OpenCV Default Behavior**: `cv2.imread()` always returns BGR
2. **AirSim Assumption**: Some assume it returns BGR (it returns RGB)
3. **Video Codec Confusion**: Different codecs may expect different formats
4. **Library Mixing**: Using OpenCV for capture and imageio for video creation
5. **Format Inheritance**: Assuming saved images maintain original format

## Verification Checklist

- [ ] Colors look realistic in generated videos
- [ ] Sky appears blue (not orange/red)
- [ ] Grass/vegetation appears green
- [ ] ML model performance is acceptable
- [ ] Video file sizes are reasonable (not over-compressed)
- [ ] Both RGB and BGR videos are available if needed

## Troubleshooting

### Issue: Colors still inverted
**Solution**: Check the entire pipeline from AirSim → save → load → video

### Issue: Video quality poor
**Solution**: Use higher quality settings in imageio or reduce compression

### Issue: ML model performs poorly
**Solution**: Ensure using RGB video (`*_rgb.mp4`) not BGR video

### Issue: Large file sizes
**Solution**: Adjust quality settings in video writer parameters

## Contact & Support

If you encounter color format issues:
1. Check this guide first
2. Verify your pipeline matches the recommended approach
3. Test with simple color patterns to isolate the issue
4. Document your specific use case and requirements

---

**Remember**: When in doubt, create both RGB and BGR videos and test which works better for your specific application! 