import os
import glob
import torch
from torch.utils.data import Dataset, DataLoader
import pytorch_lightning as pl
from utils import apply_transform_list
import random

class FireSeriesDataset(Dataset):
    def __init__(self, root_dir, img_size=112, transform=None, train=True):
        self.transform = transform
        self.sets = glob.glob(f"{root_dir}/**/*")
        self.img_size=img_size
        random.shuffle(self.sets)
        self.train = train

    def __len__(self):
        return len(self.sets)

    def __getitem__(self, idx):
        img_folder = self.sets[idx]
        img_list = glob.glob(f"{img_folder}/*.jpg")

       
        

        tensor_list = apply_transform_list(img_list, self.train)
        

        return torch.cat(tensor_list, dim=0), int(img_folder.split("/")[-2])

class FireDataModule(pl.LightningDataModule):
    def __init__(self, data_dir, batch_size=16, img_size=112, num_workers=12):
        super().__init__()
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.img_size = img_size
        self.num_workers = num_workers

    def setup(self, stage=None):
        self.train_dataset = FireSeriesDataset(
            os.path.join(self.data_dir, "train"), self.img_size, is_train=True
        )
        self.val_dataset = FireSeriesDataset(
            os.path.join(self.data_dir, "val"), self.img_size, is_train=False
        )

    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=self.batch_size, shuffle=True, num_workers=self.num_workers)

    def val_dataloader(self):
        return DataLoader(self.val_dataset, batch_size=self.batch_size, num_workers=self.num_workers)

    def test_dataloader(self):
        return DataLoader(self.val_dataset, batch_size=self.batch_size, num_workers=self.num_workers)
    
# Initialize the DataModule
data_dir = "/data/nisla/temporal_ds/images"
data_module = FireDataModule(data_dir)
data_module.setup()
# print size of the datasets

print(f"Number of training samples: {len(data_module.train_dataset)}")
print(f"Number of validation samples: {len(data_module.val_dataset)}")

