#!/usr/bin/env python3
"""
CAD Training Data Generator

Generates balanced training data with 10,000 samples per primitive shape:
- Cubes, Spheres, Cylinders, Cones, Torus

Total: 50,000 balanced samples for optimal model training.
"""

import json
import random
import math
from typing import List, Dict, Any
from pathlib import Path

class CADDataGenerator:
    def __init__(self, samples_per_primitive: int = 10000):
        self.samples_per_primitive = samples_per_primitive
        self.output_dir = Path("data")
        self.output_dir.mkdir(exist_ok=True)
        
        # Set random seed for reproducibility
        random.seed(42)
    
    def generate_cube_data(self) -> List[Dict[str, Any]]:
        """Generate 10K cube examples with diverse templates"""
        print(f"Generating {self.samples_per_primitive} cube samples...")
        
        templates = [
            "Create a box {x} by {y} by {z}",
            "Make a rectangular box {x}mm x {y}mm x {z}mm", 
            "Generate a cube with dimensions {x}, {y}, {z}",
            "Build a rectangular prism {x} by {y} by {z}",
            "Construct a cuboid {x}×{y}×{z}",
            "Create a rectangular block {x} wide, {y} deep, {z} tall",
            "Make a box with width {x}, height {y}, depth {z}",
            "Generate a rectangular solid {x}×{y}×{z}",
            "Build a cube {x} by {y} by {z} units",
            "Create a rectangular shape {x}, {y}, {z}"
        ]
        
        samples = []
        for i in range(self.samples_per_primitive):
            # Generate realistic dimensions
            x = round(random.uniform(0.1, 20.0), 2)
            y = round(random.uniform(0.1, 20.0), 2) 
            z = round(random.uniform(0.1, 20.0), 2)
            
            template = random.choice(templates)
            instruction = template.format(x=x, y=y, z=z)
            
            samples.append({
                "instruction": instruction,
                "input": "",
                "output": f"cube([{x}, {y}, {z}]);"
            })
        
        return samples
    
    def generate_sphere_data(self) -> List[Dict[str, Any]]:
        """Generate 10K sphere examples with diverse templates"""
        print(f"Generating {self.samples_per_primitive} sphere samples...")
        
        templates = [
            "Create a sphere radius {r}",
            "Generate a sphere with radius {r}",
            "Make a ball radius {r}mm",
            "Build a spherical shape r={r}",
            "Create a sphere r={r}",
            "Generate a ball with radius {r}",
            "Make a spherical object radius {r}",
            "Create a round ball r={r}",
            "Build a sphere with r={r}",
            "Generate a spherical form radius {r}"
        ]
        
        samples = []
        for i in range(self.samples_per_primitive):
            # Generate realistic radius
            r = round(random.uniform(0.1, 15.0), 2)
            
            template = random.choice(templates)
            instruction = template.format(r=r)
            
            samples.append({
                "instruction": instruction,
                "input": "",
                "output": f"sphere(r={r});"
            })
        
        return samples
    
    def generate_cylinder_data(self) -> List[Dict[str, Any]]:
        """Generate 10K cylinder examples with diverse templates"""
        print(f"Generating {self.samples_per_primitive} cylinder samples...")
        
        templates = [
            "Create a cylinder radius {r} height {h}",
            "Make a cylinder with radius {r} and height {h}",
            "Generate a cylindrical shape r={r} h={h}",
            "Build a cylinder {r}mm radius, {h}mm height", 
            "Create a cylinder r={r}, h={h}",
            "Make a cylindrical tube radius {r} height {h}",
            "Generate a cylinder with r={r} and h={h}",
            "Build a cylindrical object r={r}, h={h}",
            "Create a tube radius {r}, height {h}",
            "Make a cylindrical form r={r} h={h}"
        ]
        
        samples = []
        for i in range(self.samples_per_primitive):
            # Generate realistic dimensions
            r = round(random.uniform(0.1, 10.0), 2)
            h = round(random.uniform(0.1, 25.0), 2)
            
            template = random.choice(templates)
            instruction = template.format(r=r, h=h)
            
            samples.append({
                "instruction": instruction,
                "input": "",
                "output": f"cylinder(r={r}, h={h});"
            })
        
        return samples
    
    def generate_cone_data(self) -> List[Dict[str, Any]]:
        """Generate 10K cone examples with diverse templates"""
        print(f"Generating {self.samples_per_primitive} cone samples...")
        
        templates = [
            "Create a cone bottom radius {r1} top radius {r2} height {h}",
            "Make a cone with r1={r1}, r2={r2}, height {h}",
            "Generate a conical shape bottom {r1}, top {r2}, h={h}",
            "Build a cone {r1}mm to {r2}mm radius, {h}mm tall",
            "Create a tapered cylinder r1={r1}, r2={r2}, h={h}",
            "Make a cone from radius {r1} to {r2}, height {h}",
            "Generate a conical tube r1={r1} r2={r2} h={h}",
            "Build a cone with bottom {r1}, top {r2}, height {h}",
            "Create a truncated cone r1={r1}, r2={r2}, h={h}",
            "Make a conical shape {r1} to {r2} radius, {h} height"
        ]
        
        samples = []
        for i in range(self.samples_per_primitive):
            # Generate realistic dimensions (r1 > r2 for proper cone)
            r1 = round(random.uniform(1.0, 10.0), 2)  # Bottom radius
            r2 = round(random.uniform(0.0, r1 - 0.1), 2)  # Top radius (smaller)
            h = round(random.uniform(0.5, 20.0), 2)
            
            template = random.choice(templates)
            instruction = template.format(r1=r1, r2=r2, h=h)
            
            samples.append({
                "instruction": instruction,
                "input": "",
                "output": f"cylinder(r1={r1}, r2={r2}, h={h});"
            })
        
        return samples
    
    def generate_torus_data(self) -> List[Dict[str, Any]]:
        """Generate 10K torus examples with diverse templates"""
        print(f"Generating {self.samples_per_primitive} torus samples...")
        
        templates = [
            "Create a torus major radius {R} minor radius {r}",
            "Make a torus with R={R}, r={r}",
            "Generate a donut shape major {R}, minor {r}",
            "Build a torus {R}mm major radius, {r}mm minor radius",
            "Create a toroidal shape R={R}, r={r}",
            "Make a donut with major radius {R}, minor radius {r}",
            "Generate a torus R={R} r={r}",
            "Build a toroidal object major {R}, minor {r}",
            "Create a ring shape R={R}, r={r}",
            "Make a torus with outer {R} and inner {r} radius"
        ]
        
        samples = []
        for i in range(self.samples_per_primitive):
            # Generate realistic dimensions (R > r for proper torus)
            R = round(random.uniform(2.0, 15.0), 2)  # Major radius
            r = round(random.uniform(0.2, min(R - 0.1, 5.0)), 2)  # Minor radius (smaller)
            
            template = random.choice(templates)
            instruction = template.format(R=R, r=r)
            
            samples.append({
                "instruction": instruction,
                "input": "",
                "output": f"rotate_extrude() translate([{R},0,0]) circle(r={r});"
            })
        
        return samples
    
    def create_dataset(self) -> Dict[str, Any]:
        """Create complete balanced dataset"""
        print("="*60)
        print("CAD TRAINING DATA GENERATION")
        print("="*60)
        print(f"Generating {self.samples_per_primitive} samples per primitive...")
        print(f"Total samples: {self.samples_per_primitive * 5:,}")
        
        # Generate all primitive data
        cube_data = self.generate_cube_data()
        sphere_data = self.generate_sphere_data()
        cylinder_data = self.generate_cylinder_data()
        cone_data = self.generate_cone_data()
        torus_data = self.generate_torus_data()
        
        # Combine all data
        all_data = cube_data + sphere_data + cylinder_data + cone_data + torus_data
        
        # Shuffle for good training distribution
        random.shuffle(all_data)
        
        # Create train/test split (90/10)
        split_idx = int(0.9 * len(all_data))
        train_data = all_data[:split_idx]
        test_data = all_data[split_idx:]
        
        print(f"\nDataset Statistics:")
        print(f"  Cubes: {len(cube_data):,}")
        print(f"  Spheres: {len(sphere_data):,}")
        print(f"  Cylinders: {len(cylinder_data):,}")
        print(f"  Cones: {len(cone_data):,}")
        print(f"  Torus: {len(torus_data):,}")
        print(f"  Total: {len(all_data):,}")
        print(f"  Training: {len(train_data):,}")
        print(f"  Testing: {len(test_data):,}")
        
        return {
            "training_data": train_data,
            "test_data": test_data,
            "statistics": {
                "cubes": len(cube_data),
                "spheres": len(sphere_data), 
                "cylinders": len(cylinder_data),
                "cones": len(cone_data),
                "torus": len(torus_data),
                "total": len(all_data),
                "training_samples": len(train_data),
                "test_samples": len(test_data)
            }
        }
    
    def save_dataset(self, dataset: Dict[str, Any]):
        """Save dataset to files"""
        # Save training data
        train_file = self.output_dir / "cad_training_data.json"
        with open(train_file, 'w') as f:
            json.dump(dataset["training_data"], f, indent=2)
        print(f"\n✅ Training data saved: {train_file}")
        
        # Save test data  
        test_file = self.output_dir / "cad_test_data.json"
        with open(test_file, 'w') as f:
            json.dump(dataset["test_data"], f, indent=2)
        print(f"✅ Test data saved: {test_file}")
        
        # Save statistics
        stats_file = self.output_dir / "dataset_statistics.json"
        with open(stats_file, 'w') as f:
            json.dump(dataset["statistics"], f, indent=2)
        print(f"✅ Statistics saved: {stats_file}")
    
    def run(self):
        """Run the complete data generation process"""
        dataset = self.create_dataset()
        self.save_dataset(dataset)
        
        print("\n" + "="*60)
        print("✅ TRAINING DATA GENERATION COMPLETE!")
        print("="*60)
        print(f"Generated balanced dataset with {dataset['statistics']['total']:,} samples")
        print("Ready for model training!")

def main():
    generator = CADDataGenerator()
    generator.run()

if __name__ == "__main__":
    main()