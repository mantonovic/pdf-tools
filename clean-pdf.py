import pikepdf
import sys

def add_white_background(pdf, page):
    media_box = page["/MediaBox"]
    x0, y0 = float(media_box[0]), float(media_box[1])
    x1, y1 = float(media_box[2]), float(media_box[3])
    w, h = x1 - x0, y1 - y0

    bg_content = f"q 1 1 1 rg {x0} {y0} {w} {h} re f Q\n".encode()
    bg_stream = pikepdf.Stream(pdf, bg_content)

    if "/Contents" in page:
        contents = page["/Contents"]
        if isinstance(contents, pikepdf.Array):
            page["/Contents"] = pikepdf.Array([bg_stream] + list(contents))
        else:
            page["/Contents"] = pikepdf.Array([bg_stream, contents])
    else:
        page["/Contents"] = bg_stream

def remove_annotations_and_outline(input_pdf, output_pdf):
    """
    Remove annotations and outline from a PDF, and add a white background.
    
    Args:
        input_pdf: Path to the input PDF file
        output_pdf: Path to the output PDF file
    """
    with pikepdf.open(input_pdf) as pdf:
        for page in pdf.pages:
            # Remove all annotations
            if "/Annots" in page:
                del page["/Annots"]
            # Add white background beneath existing content
            add_white_background(pdf, page)

        # Remove all outline/bookmarks
        if "/Outlines" in pdf.Root:
            del pdf.Root["/Outlines"]

        # Save the cleaned PDF
        pdf.save(output_pdf)
        print(f"✓ Annotations removed")
        print(f"✓ Outline/Bookmarks removed")
        print(f"✓ White background added")
        print(f"✓ Saved to: {output_pdf}")

# Usage
if __name__ == "__main__":
    import os
    if len(sys.argv) == 2 and os.path.isdir(sys.argv[1]):
        directory = sys.argv[1]
        pdf_files = [f for f in os.listdir(directory)
                     if f.lower().endswith(".pdf") and not f.lower().endswith("_clean.pdf")]
        if not pdf_files:
            print("No PDF files found in directory.")
            sys.exit(0)
        for filename in sorted(pdf_files):
            input_file = os.path.join(directory, filename)
            output_file = os.path.join(directory, filename[:-4] + "_clean.pdf")
            print(f"\nProcessing: {filename}")
            remove_annotations_and_outline(input_file, output_file)
    elif len(sys.argv) == 3:
        remove_annotations_and_outline(sys.argv[1], sys.argv[2])
    else:
        print("Usage:")
        print("  python clean-pdf.py <input.pdf> <output.pdf>")
        print("  python clean-pdf.py <directory>")
        sys.exit(1)
