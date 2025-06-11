# conda-project Example

This is an example project for testing the dep-extractor tool with a Conda environment.

## Usage

1. Create and activate the conda environment:
   ```sh
   conda env create -f environment.yml
   conda activate conda-project
   ```
2. Run the example:
   ```sh
   python main.py
   ```

This will start a Flask server and print a sample pandas DataFrame.