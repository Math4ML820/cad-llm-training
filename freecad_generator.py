#!/usr/bin/env python3
"""
FreeCAD Integration Module for CAD Generation

This module provides a clean interface for creating CAD primitives and exporting
STEP files using the FreeCAD Python API.
"""

import os
import sys
from typing import Tuple, List, Optional, Dict, Any

# Add FreeCAD to Python path for macOS installation
def setup_freecad_path():
    """Setup FreeCAD Python path for macOS installation."""
    freecad_paths = [
        "/Applications/FreeCAD.app/Contents/Resources/lib",
        "/Applications/FreeCAD.app/Contents/lib", 
        "/usr/local/lib/freecad/lib",
        "/opt/homebrew/lib/freecad/lib"
    ]
    
    for path in freecad_paths:
        if os.path.exists(path) and path not in sys.path:
            sys.path.append(path)
            print(f"✅ Added FreeCAD path: {path}")
            return True
    return False

class FreeCADGenerator:
    """
    FreeCAD integration class for creating geometric primitives and exporting STEP files.
    """
    
    def __init__(self):
        self.FreeCAD = None
        self.Part = None
        self.doc = None
        self.shapes = []
        self.initialized = False
        self.use_command_mode = False
        self.freecad_cmd = None
    
    def setup_freecad(self) -> bool:
        """
        Initialize FreeCAD environment and create a new document.
        
        Returns:
            bool: True if successful, False if FreeCAD not available
        """
        # First, try to use FreeCAD via command line (more reliable for macOS)
        freecad_app = "/Applications/FreeCAD.app/Contents/MacOS/FreeCAD"
        if os.path.exists(freecad_app):
            print("✅ FreeCAD application found, using command-line mode")
            self.freecad_cmd = freecad_app
            self.use_command_mode = True
            self.initialized = True
            return True
        
        # Fallback to direct Python import
        try:
            # Setup FreeCAD path for macOS
            setup_freecad_path()
            
            # Try to import FreeCAD
            import FreeCAD
            import Part
            
            self.FreeCAD = FreeCAD
            self.Part = Part
            self.use_command_mode = False
            
            # Create a new document
            self.doc = FreeCAD.newDocument("IcemanGenerator")
            self.initialized = True
            
            print("✅ FreeCAD Python API initialized successfully")
            return True
            
        except ImportError as e:
            print(f"❌ FreeCAD not found: {e}")
            print("\n🔧 Installation Instructions:")
            print("   macOS: brew install freecad")
            print("   or download from: https://www.freecad.org/downloads.php")
            print("   Alternative: Try using FreeCAD's built-in Python console")
            return False
        except Exception as e:
            print(f"❌ Error initializing FreeCAD: {e}")
            return False
    
    def create_sphere(self, radius: float, position: Tuple[float, float, float] = (0, 0, 0), name: str = "Sphere") -> Optional[Any]:
        """
        Create a sphere primitive at the specified position.
        
        Args:
            radius: Sphere radius
            position: (x, y, z) position tuple
            name: Object name in FreeCAD document
            
        Returns:
            FreeCAD object or None if failed
        """
        if not self.initialized:
            print("❌ FreeCAD not initialized. Call setup_freecad() first.")
            return None
            
        try:
            # Create sphere shape
            sphere_shape = self.Part.makeSphere(radius)
            
            # Create FreeCAD object
            sphere_obj = self.doc.addObject("Part::Feature", name)
            sphere_obj.Shape = sphere_shape
            
            # Position the sphere
            sphere_obj.Placement.Base = self.FreeCAD.Vector(position[0], position[1], position[2])
            
            self.shapes.append(sphere_obj)
            print(f"✅ Created sphere '{name}' - radius: {radius}, position: {position}")
            
            return sphere_obj
            
        except Exception as e:
            print(f"❌ Error creating sphere '{name}': {e}")
            return None
    
    def create_cube(self, dimensions: Tuple[float, float, float], position: Tuple[float, float, float] = (0, 0, 0), name: str = "Cube") -> Optional[Any]:
        """
        Create a cube primitive at the specified position.
        
        Args:
            dimensions: (length, width, height) tuple
            position: (x, y, z) position tuple
            name: Object name in FreeCAD document
            
        Returns:
            FreeCAD object or None if failed
        """
        if not self.initialized:
            print("❌ FreeCAD not initialized. Call setup_freecad() first.")
            return None
            
        try:
            # Create box shape (cube)
            box_shape = self.Part.makeBox(dimensions[0], dimensions[1], dimensions[2])
            
            # Create FreeCAD object
            box_obj = self.doc.addObject("Part::Feature", name)
            box_obj.Shape = box_shape
            
            # Position the cube (adjust for center positioning)
            center_x = position[0] - dimensions[0] / 2
            center_y = position[1] - dimensions[1] / 2
            center_z = position[2]
            box_obj.Placement.Base = self.FreeCAD.Vector(center_x, center_y, center_z)
            
            self.shapes.append(box_obj)
            print(f"✅ Created cube '{name}' - dimensions: {dimensions}, position: {position}")
            
            return box_obj
            
        except Exception as e:
            print(f"❌ Error creating cube '{name}': {e}")
            return None
    
    def create_freecad_script(self, output_filename: str) -> str:
        """
        Generate a FreeCAD Python script to create the iceman model.
        
        Args:
            output_filename: Output STEP file name
            
        Returns:
            str: FreeCAD Python script content
        """
        script = f'''#!/usr/bin/env python3
"""
FreeCAD Script to Generate Iceman Model
Auto-generated by freecad_generator.py
"""

import FreeCAD
import Part
import os

def create_iceman():
    # Create new document
    doc = FreeCAD.newDocument("IcemanGenerator")
    
    print("Creating Iceman Assembly...")
    
    # Create the three main spheres (snowman body)
    base_sphere = Part.makeSphere(3.0)
    base_obj = doc.addObject("Part::Feature", "Base_Sphere")
    base_obj.Shape = base_sphere
    base_obj.Placement.Base = FreeCAD.Vector(0, 0, 3.0)
    
    middle_sphere = Part.makeSphere(2.0)
    middle_obj = doc.addObject("Part::Feature", "Middle_Sphere")
    middle_obj.Shape = middle_sphere
    middle_obj.Placement.Base = FreeCAD.Vector(0, 0, 7.0)
    
    head_sphere = Part.makeSphere(1.5)
    head_obj = doc.addObject("Part::Feature", "Head_Sphere")
    head_obj.Shape = head_sphere
    head_obj.Placement.Base = FreeCAD.Vector(0, 0, 10.0)
    
    print("✅ Created main spheres")
    
    # Create cube accessories
    # Eyes (2 small cubes on head)
    left_eye_shape = Part.makeBox(0.2, 0.2, 0.2)
    left_eye = doc.addObject("Part::Feature", "Left_Eye")
    left_eye.Shape = left_eye_shape
    left_eye.Placement.Base = FreeCAD.Vector(-0.6, 1.1, 10.4)
    
    right_eye_shape = Part.makeBox(0.2, 0.2, 0.2)
    right_eye = doc.addObject("Part::Feature", "Right_Eye")
    right_eye.Shape = right_eye_shape
    right_eye.Placement.Base = FreeCAD.Vector(0.4, 1.1, 10.4)
    
    # Nose (carrot-like cube)
    nose_shape = Part.makeBox(0.3, 0.8, 0.3)
    nose = doc.addObject("Part::Feature", "Nose")
    nose.Shape = nose_shape
    nose.Placement.Base = FreeCAD.Vector(-0.15, 1.35, 9.85)
    
    # Buttons (3 cubes down the middle)
    button1_shape = Part.makeBox(0.3, 0.3, 0.2)
    button1 = doc.addObject("Part::Feature", "Button_1")
    button1.Shape = button1_shape
    button1.Placement.Base = FreeCAD.Vector(-0.15, 1.65, 7.4)
    
    button2_shape = Part.makeBox(0.3, 0.3, 0.2)
    button2 = doc.addObject("Part::Feature", "Button_2")
    button2.Shape = button2_shape
    button2.Placement.Base = FreeCAD.Vector(-0.15, 1.65, 6.9)
    
    button3_shape = Part.makeBox(0.3, 0.3, 0.2)
    button3 = doc.addObject("Part::Feature", "Button_3")
    button3.Shape = button3_shape
    button3.Placement.Base = FreeCAD.Vector(-0.15, 1.65, 6.4)
    
    # Hat (rectangular cube on top of head)
    hat_shape = Part.makeBox(3.0, 3.0, 0.8)
    hat = doc.addObject("Part::Feature", "Hat")
    hat.Shape = hat_shape
    hat.Placement.Base = FreeCAD.Vector(-1.5, -1.5, 11.7)
    
    print("✅ Created all accessories")
    
    # Recompute the document
    doc.recompute()
    
    # Export to STEP file
    objects = doc.Objects
    output_file = "{output_filename}"
    
    print(f"📁 Exporting to: {{os.path.abspath(output_file)}}")
    Part.export(objects, output_file)
    
    # Verify file was created
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file)
        print(f"✅ STEP file exported successfully!")
        print(f"   File: {{os.path.abspath(output_file)}}")
        print(f"   Size: {{file_size:,}} bytes")
        print(f"   Objects: {{len(objects)}}")
        return True
    else:
        print("❌ STEP file was not created")
        return False

if __name__ == "__main__":
    create_iceman()
'''
        return script
    
    def run_freecad_script(self, script_content: str, output_filename: str) -> bool:
        """
        Execute FreeCAD script using command line mode.
        
        Args:
            script_content: Python script to execute
            output_filename: Expected output file
            
        Returns:
            bool: True if successful
        """
        import tempfile
        import subprocess
        
        # Create temporary script file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script_content)
            script_path = f.name
        
        try:
            print("🚀 Running FreeCAD in command-line mode...")
            
            # Use the working method: echo exec command | FreeCAD --console
            exec_cmd = f"exec(open('{script_path}').read())"
            
            cmd = f'echo "{exec_cmd}" | "{self.freecad_cmd}" --console'
            
            result = subprocess.run(
                cmd, 
                shell=True,
                capture_output=True, 
                text=True, 
                timeout=120,
                cwd=os.getcwd()
            )
            
            # Parse output for success indicators
            if result.stdout:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'SUCCESS: STEP file exported!' in line:
                        print("✅ STEP file exported successfully!")
                    elif 'File:' in line and output_filename in line:
                        print(f"📁 {line.strip()}")
                    elif 'Size:' in line:
                        print(f"📊 {line.strip()}")
                    elif 'Objects:' in line:
                        print(f"🔧 {line.strip()}")
            
            if result.stderr and 'Error:' in result.stderr:
                # Show only actual errors, not the 3Dconnexion warning
                error_lines = [line for line in result.stderr.split('\n') 
                              if 'Error:' in line and '3DconnexionNavlib' not in line]
                if error_lines:
                    print("⚠️  Warnings/Errors:")
                    for line in error_lines:
                        print(f"   {line}")
            
            # Check if output file was created
            if os.path.exists(output_filename):
                file_size = os.path.getsize(output_filename)
                print(f"✅ Output file created: {os.path.abspath(output_filename)} ({file_size:,} bytes)")
                return True
            else:
                print(f"❌ Output file '{output_filename}' not found")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ FreeCAD execution timed out")
            return False
        except Exception as e:
            print(f"❌ Error running FreeCAD script: {e}")
            return False
        finally:
            # Clean up temporary file
            try:
                os.unlink(script_path)
            except:
                pass

    def assemble_iceman(self) -> bool:
        """
        Create a complete iceman assembly with spheres and cubes.
        
        Returns:
            bool: True if successful
        """
        if not self.initialized:
            print("❌ FreeCAD not initialized. Call setup_freecad() first.")
            return False
        
        # If using command mode, defer to export_step method
        if self.use_command_mode:
            print("✅ Iceman assembly prepared for command-line generation")
            return True
        
        print("\n🎿 Creating Iceman Assembly...")
        
        try:
            # Create the three main spheres (snowman body)
            base_sphere = self.create_sphere(3.0, (0, 0, 3.0), "Base_Sphere")
            middle_sphere = self.create_sphere(2.0, (0, 0, 7.0), "Middle_Sphere")
            head_sphere = self.create_sphere(1.5, (0, 0, 10.0), "Head_Sphere")
            
            if not all([base_sphere, middle_sphere, head_sphere]):
                print("❌ Failed to create main spheres")
                return False
            
            # Create cube accessories
            # Eyes (2 small cubes on head)
            left_eye = self.create_cube((0.2, 0.2, 0.2), (-0.5, 1.2, 10.5), "Left_Eye")
            right_eye = self.create_cube((0.2, 0.2, 0.2), (0.5, 1.2, 10.5), "Right_Eye")
            
            # Nose (carrot-like cube)
            nose = self.create_cube((0.3, 0.8, 0.3), (0, 1.5, 10.0), "Nose")
            
            # Buttons (3 cubes down the middle)
            button1 = self.create_cube((0.3, 0.3, 0.2), (0, 1.8, 7.5), "Button_1")
            button2 = self.create_cube((0.3, 0.3, 0.2), (0, 1.8, 7.0), "Button_2")
            button3 = self.create_cube((0.3, 0.3, 0.2), (0, 1.8, 6.5), "Button_3")
            
            # Hat (rectangular cube on top of head)
            hat = self.create_cube((3.0, 3.0, 0.8), (0, 0, 11.8), "Hat")
            
            # Recompute the document
            self.doc.recompute()
            
            print("🎉 Iceman assembly completed successfully!")
            print(f"   Total shapes created: {len(self.shapes)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error assembling iceman: {e}")
            return False
    
    def export_step(self, filename: str = "iceman.stp") -> bool:
        """
        Export all shapes to a STEP file.
        
        Args:
            filename: Output filename (with or without .stp extension)
            
        Returns:
            bool: True if export successful
        """
        if not self.initialized:
            print("❌ FreeCAD not initialized. Call setup_freecad() first.")
            return False
        
        # Ensure .stp extension
        if not filename.endswith('.stp') and not filename.endswith('.step'):
            filename += '.stp'
        
        # Use command-line mode if available
        if self.use_command_mode:
            print(f"\n📁 Generating STEP file using FreeCAD command-line: {filename}")
            script = self.create_freecad_script(filename)
            return self.run_freecad_script(script, filename)
        
        # Use Python API mode
        if not self.shapes:
            print("❌ No shapes to export. Create geometry first.")
            return False
        
        try:
            # Get full path
            full_path = os.path.abspath(filename)
            
            print(f"\n📁 Exporting to STEP file: {full_path}")
            
            # Export all shapes to STEP format
            self.Part.export(self.shapes, full_path)
            
            # Verify file was created
            if os.path.exists(full_path):
                file_size = os.path.getsize(full_path)
                print(f"✅ STEP file exported successfully!")
                print(f"   File: {full_path}")
                print(f"   Size: {file_size:,} bytes")
                print(f"   Objects exported: {len(self.shapes)}")
                return True
            else:
                print("❌ STEP file was not created")
                return False
                
        except Exception as e:
            print(f"❌ Error exporting STEP file: {e}")
            return False
    
    def get_shapes_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all created shapes.
        
        Returns:
            List of shape information dictionaries
        """
        info_list = []
        for shape in self.shapes:
            info = {
                'name': shape.Label,
                'type': shape.TypeId,
                'position': (shape.Placement.Base.x, shape.Placement.Base.y, shape.Placement.Base.z),
                'volume': shape.Shape.Volume if hasattr(shape.Shape, 'Volume') else 0
            }
            info_list.append(info)
        return info_list
    
    def cleanup(self):
        """Clean up FreeCAD document and resources."""
        if self.doc and self.FreeCAD:
            try:
                self.FreeCAD.closeDocument(self.doc.Name)
                print("🧹 FreeCAD document cleaned up")
            except:
                pass
    
    def __del__(self):
        """Destructor - cleanup resources."""
        self.cleanup()


def create_iceman_stp(output_filename: str = "iceman.stp") -> bool:
    """
    Convenience function to create a complete iceman and export to STP file.
    Uses direct FreeCAD command-line approach for maximum compatibility.
    
    Args:
        output_filename: Output STEP file name
        
    Returns:
        bool: True if successful
    """
    import subprocess
    import os
    
    # Check if FreeCAD is available
    freecad_cmd = "/Applications/FreeCAD.app/Contents/MacOS/FreeCAD"
    if not os.path.exists(freecad_cmd):
        print("❌ FreeCAD not found at expected location")
        print("💡 Please install FreeCAD from https://www.freecad.org/")
        return False
    
    # Create the FreeCAD script content (ASCII only)
    script_content = f'''
import FreeCAD
import Part
import os

# Create new document
doc = FreeCAD.newDocument("IcemanGenerator")

print("Creating Iceman Assembly...")

# Create the three main spheres (snowman body)
base_sphere = Part.makeSphere(3.0)
base_obj = doc.addObject("Part::Feature", "Base_Sphere")
base_obj.Shape = base_sphere
base_obj.Placement.Base = FreeCAD.Vector(0, 0, 3.0)

middle_sphere = Part.makeSphere(2.0)
middle_obj = doc.addObject("Part::Feature", "Middle_Sphere")
middle_obj.Shape = middle_sphere
middle_obj.Placement.Base = FreeCAD.Vector(0, 0, 7.0)

head_sphere = Part.makeSphere(1.5)
head_obj = doc.addObject("Part::Feature", "Head_Sphere")
head_obj.Shape = head_sphere
head_obj.Placement.Base = FreeCAD.Vector(0, 0, 10.0)

print("Created main spheres")

# Create cube accessories
# Eyes (2 small cubes on head)
left_eye_shape = Part.makeBox(0.2, 0.2, 0.2)
left_eye = doc.addObject("Part::Feature", "Left_Eye")
left_eye.Shape = left_eye_shape
left_eye.Placement.Base = FreeCAD.Vector(-0.6, 1.1, 10.4)

right_eye_shape = Part.makeBox(0.2, 0.2, 0.2)
right_eye = doc.addObject("Part::Feature", "Right_Eye")
right_eye.Shape = right_eye_shape
right_eye.Placement.Base = FreeCAD.Vector(0.4, 1.1, 10.4)

# Nose (carrot-like cube)
nose_shape = Part.makeBox(0.3, 0.8, 0.3)
nose = doc.addObject("Part::Feature", "Nose")
nose.Shape = nose_shape
nose.Placement.Base = FreeCAD.Vector(-0.15, 1.35, 9.85)

# Buttons (3 cubes down the middle)
button1_shape = Part.makeBox(0.3, 0.3, 0.2)
button1 = doc.addObject("Part::Feature", "Button_1")
button1.Shape = button1_shape
button1.Placement.Base = FreeCAD.Vector(-0.15, 1.65, 7.4)

button2_shape = Part.makeBox(0.3, 0.3, 0.2)
button2 = doc.addObject("Part::Feature", "Button_2")
button2.Shape = button2_shape
button2.Placement.Base = FreeCAD.Vector(-0.15, 1.65, 6.9)

button3_shape = Part.makeBox(0.3, 0.3, 0.2)
button3 = doc.addObject("Part::Feature", "Button_3")
button3.Shape = button3_shape
button3.Placement.Base = FreeCAD.Vector(-0.15, 1.65, 6.4)

# Hat (rectangular cube on top of head)
hat_shape = Part.makeBox(3.0, 3.0, 0.8)
hat = doc.addObject("Part::Feature", "Hat")
hat.Shape = hat_shape
hat.Placement.Base = FreeCAD.Vector(-1.5, -1.5, 11.7)

print("Created all accessories")

# Recompute the document
doc.recompute()

# Export to STEP file
objects = doc.Objects
output_file = "{output_filename}"

print("Exporting to: " + os.path.abspath(output_file))
Part.export(objects, output_file)

# Verify file was created
if os.path.exists(output_file):
    file_size = os.path.getsize(output_file)
    print("SUCCESS: STEP file exported!")
    print("File: " + os.path.abspath(output_file))
    print("Size: " + str(file_size) + " bytes")
    print("Objects: " + str(len(objects)))
else:
    print("ERROR: STEP file was not created")
'''
    
    # Write script to temporary file
    script_file = "temp_iceman_script.py"
    
    try:
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        print(f"Creating iceman STEP file: {output_filename}")
        print("Running FreeCAD...")
        
        # Execute with FreeCAD using the working method
        exec_command = f"exec(open('{script_file}').read())"
        cmd = f'echo "{exec_command}" | "{freecad_cmd}" --console'
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        
        # Show relevant output
        if result.stdout:
            lines = result.stdout.split('\n')
            for line in lines:
                if any(keyword in line for keyword in ['Creating', 'Created', 'Exporting', 'SUCCESS', 'File:', 'Size:', 'Objects:']):
                    print(line.strip())
        
        # Check if file was created
        if os.path.exists(output_filename):
            size = os.path.getsize(output_filename)
            print(f"\n🎉 SUCCESS: Iceman created and exported to '{output_filename}' ({size:,} bytes)")
            return True
        else:
            print(f"\n❌ ERROR: {output_filename} was not created")
            return False
            
    except Exception as e:
        print(f"❌ Error in iceman creation: {e}")
        return False
    finally:
        # Clean up temporary file
        if os.path.exists(script_file):
            try:
                os.remove(script_file)
            except:
                pass


if __name__ == "__main__":
    """
    Direct script execution - create iceman STP file.
    """
    print("🎿 CAD Iceman Generator")
    print("=" * 50)
    
    success = create_iceman_stp("iceman.stp")
    
    if success:
        print("\n✨ Ready to open in your favorite CAD software!")
    else:
        print("\n💡 Make sure FreeCAD is installed and try again.")
    
    sys.exit(0 if success else 1)