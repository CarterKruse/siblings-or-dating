import torch
import numpy as np
from PIL import Image
import dnnlib
import legacy
from torchvision import transforms

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load the pre-trained StyleGAN2 model
def load_stylegan2_model(model_path):
    with dnnlib.util.open_url(model_path) as f:
        G = legacy.load_network_pkl(f)['G_ema'].to(device)
    return G

# Generate an image from a latent vector
def generate_image_from_latent(G, latent_vector):
    # Convert latent vector to a torch tensor
    latent_vector = torch.from_numpy(latent_vector).to(device)

    # Generate the image
    img = G.synthesis(latent_vector.unsqueeze(0), noise_mode='const')
    img = (img + 1) / 2 # Normalize to [0, 1]
    img = img.clamp(0, 1)

    # Convert tensor to PIL image
    pil_image = transforms.toPILImage()(img[0].cpu())
    return pil_image

# Perturb the latent vector slightly to generate a new image
def perturb_latent(latent_vector, perturbation_strength=0.1):
    perturbation = np.random.randn(*latent_vector.shape) * perturbation_strength
    return latent_vector + perturbation

if __name__ == "__main__":
    # Path to the pre-trained StyleGAN2 model
    model_path = 'path.pkl'

    # Load StyleGAN2 model
    G = load_stylegan2_model(model_path)

    # Define the initial latent vector (using a random one for simplicity)
    latent_base = np.random.randn(1, 512)

    # Generate a sequence of similar faces
    num_steps = 10
    for i in range(num_steps):
        # Perturb the latent vector to generate a new face
        latent_new = perturb_latent(latent_base, perturbation_strength=0.05*num_steps)

        # Generate and save the image
        face_img = generate_image_from_latent(G, latent_new)
        face_img.save(f'generated_faces/generated_face_{i+1}.png')
        print(f'Generated face {i+1}')

