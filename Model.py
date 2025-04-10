import torch
import torchvision.transforms as transforms
from PIL import Image
from torchvision.transforms import v2 as transforms
from torchvision import datasets
from torch.utils.data import Dataset, DataLoader
from typing import Optional, List, Tuple, Sequence, Union
from torchvision.transforms.v2.functional import resize
import torch
import torch.nn as nn
import torchvision.transforms.functional as F
import scipy
from pathlib import Path
import os
from torchvision import models
import matplotlib.pyplot as plt
# Классы
class MatResize(nn.Module):
  def __init__(self, size: Union[List, Tuple], interpolation='bilinear') -> None:
    super().__init__()
    self.size = size
    self.interpolation = interpolation

  def forward(self, img: torch.Tensor) -> torch.Tensor:
    return resize(img, self.size)

def load_model(checkpoint_path: str, model: torch.nn.Module, device: torch.device):
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()
    print(f"Модель загружена из {checkpoint_path}")
    return model

class MatCenterCrop(nn.Module):
    def __init__(self, size: Union[int, Tuple[int, int]]) -> None:
        super().__init__()
        self.size = size

    def forward(self, img: torch.Tensor) -> torch.Tensor:
        if isinstance(self.size, int):
            return F.center_crop(img, self.size)
        else:
            return F.center_crop(img, self.size)

class MatNormalize(nn.Module):
  def __init__(self, mean: Sequence[float], std: Sequence[float], inplace: bool=False) -> None:
    super().__init__()
    self.mean = mean
    self.std = std
    self.inplace = inplace

  def forward(self, tensor: torch.Tensor) -> torch.Tensor:
    if not self.inplace:
        tensor = tensor.clone()

    dtype = tensor.dtype
    mean = torch.as_tensor(self.mean, dtype=dtype, device=tensor.device)
    std = torch.as_tensor(self.std, dtype=dtype, device=tensor.device)

    if (std == 0).any():
        raise ValueError(f"std evaluated to zero after conversion to {dtype}, leading to division by zero.")

    if mean.ndim == 1:
        mean = mean.view(-1, 1, 1)
    if std.ndim == 1:
        std = std.view(-1, 1, 1)

    return tensor.sub_(mean).div_(std)

class HyperSpectralDataset(Dataset):
    def __init__(self, root: Union[str, Path], transforms = None, dtype = torch.float) -> None:
        self.folder_path = root
        self.paths = list(Path(root).glob('*/*.mat'))
        self.transforms = transforms
        self.dtype = dtype
        self.classes = sorted(os.listdir(root))

    def __len__(self) -> int:
        return len(self.paths)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.float]:
        file_path = self.paths[idx]
        class_name = file_path.parent.name
        class_idx = torch.tensor(self.classes.index(class_name), dtype=torch.float)

        # Загрузка .mat файла
        mat_data = scipy.io.loadmat(file_path).get('DataCubeC')

        # Перестановка осей
        # Из (height, width, channels) в (channels, height, width)
        hyperspectral_image = torch.tensor(mat_data, dtype=self.dtype)
        hyperspectral_image = hyperspectral_image.permute(2, 0, 1)

        # Преобразуем значения к [0, 1]
        min_val = hyperspectral_image.min()
        max_val = hyperspectral_image.max()
        hyperspectral_image = (hyperspectral_image - min_val) / (max_val - min_val)

        if self.transforms:
          hyperspectral_image = self.transforms(hyperspectral_image)

        return (hyperspectral_image, class_idx)

def plot_one_layer(path):
    image = scipy.io.loadmat(path)['DataCubeC']
    first_layer = image[:, :, 0]  # Отображаем первый канал (слой)
    filename = os.path.splitext(os.path.basename(path))[0]
    save_path_e = os.path.join('Photos/', f"{filename}_layer0.png")
    plt.imshow(first_layer, cmap='gray')  # Отображаем слой в серых тонах
    plt.axis('off')  # Отключаем оси
    plt.title('Первый слой изображения')
    plt.savefig(f'{save_path_e}', bbox_inches='tight', pad_inches=0)
    return save_path_e


def predict(model: torch.nn.Module, transform, threshold: float, device: torch.device, file_path: str):

    mat_file = str(Path(file_path))

    mat_data = scipy.io.loadmat(mat_file).get('DataCubeC')

        # Преобразуем в тензор и переставляем оси (C, H, W)
    image = torch.tensor(mat_data, dtype=torch.float).permute(2, 0, 1)

        # Применяем трансформации
    image = transform(image).unsqueeze(0).to(device)
                # Предсказание
    model.eval()
    with torch.inference_mode():
            output = model(image).squeeze().sigmoid()
            probability = output.item() * 100
            prediction = 1 if output >= threshold else 0

    return (prediction, probability)

def path_to_file(path):  # Укажи полный путь к конкретному файлу
    photo = plot_one_layer(path)
    prediction, probability = predict(model, transform, file_path=path, threshold=0.4, device=device)
    return ( photo, prediction, probability)

def editted_efficientnet_b1(weights_path:str, in_channels:16, out_features: int =1) -> nn.Module:
    weights2 = torch.load('weights/efficientnet_b1_best.pt', weights_only=True)

    # Изменим модель, чтобы веса "встали"
    model2 = models.efficientnet_b1()
    model2.classifier[1] = nn.Linear(in_features=1280, out_features=9, bias=True)
    model2.load_state_dict(weights2)

    # Заморозим параметры
    for param in model2.parameters():
        param.requires_grad = False

    # Адаптируем под нашу задачу
    model2.features[0][0] = nn.Conv2d(
    in_channels=16,
    out_channels=32,
    kernel_size=(3, 3),
    stride=(2, 2),
    padding=(1, 1),
    bias=False,
    )
    model2.classifier[1] = nn.Linear(in_features=1280, out_features=1, bias=True)
    return model2
# Инициализация устройства
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Создаём модель
#model = model2  # вот эта фигня
model2=editted_efficientnet_b1('weights/efficientnet_b1_best.pt', 16)
model = load_model("model/best_model.pth", model2, device)

transform = transforms.Compose([
    MatCenterCrop((200, 500)),
    MatResize(size=(255, 255)),
    MatNormalize(mean=0.456, std=0.224)
])


