#!/usr/bin/env python3
"""
Iceman Demo - Interactive STEP File Generator

This script provides an interactive interface for generating iceman CAD models
and exporting them as .stp files using FreeCAD.
"""

import os
import sys
import time
from typing import Optional

# Import our FreeCAD generator
from freecad_generator import FreeCADGenerator, create_iceman_stp


class IcemanDemo:
    """
    Interactive demo class for creating iceman STEP files.
    """
    
    def __init__(self):
        self.generator = None
    
    def display_banner(self):
        """Display the application banner."""
        print("\n" + "=" * 60)
        print("🎿  CAD ICEMAN GENERATOR - STEP FILE CREATOR  ⛄")
        print("=" * 60)
        print("Create classic snowman-style iceman models as .stp files")
        print("Compatible with FreeCAD, Fusion 360, SolidWorks, and more!")
        print("=" * 60)
    
    def check_freecad_status(self) -> bool:
        """
        Check if FreeCAD is available and display status.
        
        Returns:
            bool: True if FreeCAD is available
        """
        print("\n🔍 Checking FreeCAD installation...")
        
        # Check for FreeCAD application (more reliable than Python import)
        import os
        freecad_app = "/Applications/FreeCAD.app/Contents/MacOS/FreeCAD"
        if os.path.exists(freecad_app):
            print("✅ FreeCAD Application: Available")
            print("✅ Using command-line mode for compatibility")
            return True
            
        # Fallback to Python API check
        try:
            import FreeCAD
            import Part
            print("✅ FreeCAD Python API: Available")
            print(f"✅ FreeCAD Version: {FreeCAD.Version()}")
            return True
        except ImportError:
            print("❌ FreeCAD not found")
            print("\n💡 Installation Required:")
            print("   macOS:     brew install freecad")
            print("   Windows:   Download from https://www.freecad.org/")
            print("   Linux:     sudo apt install freecad  (or equivalent)")
            print("   Python:    pip install freecad")
            return False
    
    def display_iceman_specs(self):
        """Display the iceman design specifications."""
        print("\n📐 ICEMAN DESIGN SPECIFICATIONS")
        print("-" * 40)
        print("🔵 Base Sphere:     Radius 3.0  (Bottom)")
        print("🔵 Middle Sphere:   Radius 2.0  (Torso)")
        print("🔵 Head Sphere:     Radius 1.5  (Head)")
        print("🔳 Eyes:           2x Small cubes")
        print("🔳 Nose:           Carrot-style cube")
        print("🔳 Buttons:        3x Round buttons")
        print("🔳 Hat:            Top hat cube")
        print("-" * 40)
        print("📏 Total Height:    ~12 units")
        print("📏 Base Width:      6 units (diameter)")
    
    def get_output_filename(self) -> str:
        """
        Get output filename from user with validation.
        
        Returns:
            str: Validated output filename
        """
        while True:
            print("\n📁 OUTPUT FILE SETTINGS")
            print("-" * 30)
            
            # Get filename
            filename = input("Enter output filename (or press Enter for 'iceman.stp'): ").strip()
            
            if not filename:
                filename = "iceman.stp"
            
            # Ensure .stp extension
            if not filename.endswith('.stp') and not filename.endswith('.step'):
                filename += '.stp'
            
            # Check if file exists
            if os.path.exists(filename):
                print(f"⚠️  File '{filename}' already exists!")
                overwrite = input("Overwrite? (y/n): ").strip().lower()
                if overwrite in ['y', 'yes']:
                    break
                else:
                    continue
            else:
                break
        
        return filename
    
    def create_iceman_with_progress(self, filename: str) -> bool:
        """
        Create iceman with progress display.
        
        Args:
            filename: Output filename
            
        Returns:
            bool: True if successful
        """
        print(f"\n🚀 CREATING ICEMAN MODEL")
        print("=" * 40)
        
        try:
            print("⏳ Step 1/3: Preparing FreeCAD script...")
            time.sleep(0.5)  # Brief pause for user experience
            
            print("⏳ Step 2/3: Running FreeCAD and creating geometry...")
            
            # Use the working create_iceman_stp function
            from freecad_generator import create_iceman_stp
            success = create_iceman_stp(filename)
            
            if not success:
                return False
            
            time.sleep(0.5)
            
            print("⏳ Step 3/3: Validating output...")
            
            # Validate output file
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                print(f"✅ Validation complete!")
                print(f"   File size: {file_size:,} bytes")
                print(f"   Location: {os.path.abspath(filename)}")
                print(f"   Components: 8 geometric objects (3 spheres + 5 cubes)")
                return True
            else:
                print("❌ Output file not found after export")
                return False
                
        except Exception as e:
            print(f"❌ Error during creation: {e}")
            return False
    
    def display_success_info(self, filename: str):
        """Display success information and next steps."""
        print("\n" + "🎉" * 20)
        print("SUCCESS! Your iceman is ready!")
        print("🎉" * 20)
        
        full_path = os.path.abspath(filename)
        print(f"\n📁 File Location: {full_path}")
        
        print(f"\n🔧 Compatible CAD Software:")
        print("   • FreeCAD (Free) - https://www.freecad.org/")
        print("   • Fusion 360 (Free for personal)")
        print("   • SolidWorks")
        print("   • AutoCAD")
        print("   • OnShape (Web-based)")
        print("   • Any STEP-compatible CAD viewer")
        
        print(f"\n💡 Next Steps:")
        print(f"   1. Open '{filename}' in your CAD software")
        print("   2. View and rotate the 3D model")
        print("   3. Modify, 3D print, or use as reference")
    
    def display_shape_details(self):
        """Display detailed information about created shapes."""
        if not self.generator or not self.generator.shapes:
            return
        
        print(f"\n📊 DETAILED SHAPE INFORMATION")
        print("-" * 50)
        
        shapes_info = self.generator.get_shapes_info()
        
        for i, info in enumerate(shapes_info, 1):
            print(f"{i:2d}. {info['name']}")
            print(f"     Type: {info['type']}")
            print(f"     Position: ({info['position'][0]:.1f}, {info['position'][1]:.1f}, {info['position'][2]:.1f})")
            if info['volume'] > 0:
                print(f"     Volume: {info['volume']:.2f} cubic units")
    
    def run_interactive_mode(self):
        """Run the interactive demo mode."""
        self.display_banner()
        
        # Check FreeCAD
        if not self.check_freecad_status():
            print("\n❌ Cannot continue without FreeCAD. Please install and try again.")
            return False
        
        # Display specifications
        self.display_iceman_specs()
        
        # Get user confirmation to proceed
        print(f"\n🚀 Ready to create your iceman!")
        proceed = input("Continue? (y/n): ").strip().lower()
        
        if proceed not in ['y', 'yes']:
            print("👋 Demo cancelled. Come back anytime!")
            return False
        
        # Get output filename
        filename = self.get_output_filename()
        
        # Create the iceman
        success = self.create_iceman_with_progress(filename)
        
        if success:
            self.display_success_info(filename)
            
            # Ask if user wants to see detailed info
            show_details = input("\nShow detailed shape information? (y/n): ").strip().lower()
            if show_details in ['y', 'yes']:
                self.display_shape_details()
        
        return success
    
    def run_batch_mode(self, filename: str) -> bool:
        """
        Run in batch mode (non-interactive).
        
        Args:
            filename: Output filename
            
        Returns:
            bool: True if successful
        """
        print("🎿 CAD Iceman Generator - Batch Mode")
        print("=" * 40)
        
        from freecad_generator import create_iceman_stp
        return create_iceman_stp(filename)


def main():
    """Main application entry point."""
    
    # Check command line arguments
    if len(sys.argv) > 1:
        # Batch mode - filename provided as argument
        filename = sys.argv[1]
        demo = IcemanDemo()
        success = demo.run_batch_mode(filename)
        sys.exit(0 if success else 1)
    else:
        # Interactive mode
        demo = IcemanDemo()
        success = demo.run_interactive_mode()
        
        if success:
            print(f"\n✨ Thank you for using CAD Iceman Generator!")
        else:
            print(f"\n💭 Try again when ready. We'll be here!")
        
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()