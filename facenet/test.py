import torch
import torch.nn.functional as F
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
import matplotlib.pyplot as plt

# Initialize the MTCNN module for face detection and the InceptionResnetV1 module for face embedding
mtcnn = MTCNN(image_size=160, keep_all=True)
resnet = InceptionResnetV1(pretrained='vggface2').eval()

def get_embedding(image_path):
    '''load an image, detect the face, and return the embedding and face'''
    try:
        image = Image.open(image_path).convert('RGB')
    except Exception as e:
        print(f'Error loading image from {image_path}: {e}')
        return None
    
    # Detect faces in the image
    faces, _ = mtcnn(image, return_prob=True)
    if faces is None or len(faces) == 0:
        print('No faces detected.')
        return None
    
    # Get the embedding for the first detected face
    embedding = resnet(faces[0].unsqueeze(0))
    return embedding

def cosine_similarity(embedding1, embedding2):
    '''compute cosine similarity between two embeddings'''
    similarity = F.cosine_similarity(embedding1, embedding2)
    return similarity.item()

embedding1 = get_embedding('./test_faces/test_1.png')
embedding2 = get_embedding('./test_faces/test_2.png')
print('Difference similarity:', cosine_similarity(embedding1, embedding2))

embedding3 = get_embedding('./test_faces/test_3.png')
embedding4 = get_embedding('./test_faces/test_4.png')
print('Similar similarity:', cosine_similarity(embedding3, embedding4))

emma_stone1 = get_embedding('./test_faces/emma_stone_1.png')
emma_stone2 = get_embedding('./test_faces/emma_stone_2.png')
print('Emma stone similarity:', cosine_similarity(emma_stone1, emma_stone2))

print('Difference similarity:', cosine_similarity(embedding1, emma_stone2))
print('Difference similarity:', cosine_similarity(embedding2, emma_stone2))
print('Difference similarity:', cosine_similarity(embedding3, emma_stone2))
print('Difference similarity:', cosine_similarity(embedding4, emma_stone2))
