import numpy as np
from insightface.app import FaceAnalysis

# Initialize once (important for performance)
app = FaceAnalysis(name="buffalo_s",
                    providers=["CPUExecutionProvider"],
                   allowed_modules=['detection','recognition'])
app.prepare(ctx_id=0,det_size=(320,320))  # CPU-0 and 1-gpu(auto-detect)

def get_face_embedding(frame):
    faces = app.get(frame)

    if not faces:
        return None, None, 0

    # return only the strongest face
    faces = sorted(faces, key=lambda f: f.det_score, reverse=True)
    face = faces[0]

    return face.normed_embedding, face.bbox.astype(int), len(faces)

