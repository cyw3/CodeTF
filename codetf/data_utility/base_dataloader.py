import multiprocessing
from torch.utils.data import TensorDataset
import torch
import concurrent.futures
from omegaconf import OmegaConf
from codetf.common.utils import get_abs_path
from torch.utils.data import IterableDataset, Dataset

class BaseDataLoader():
    
    DATASET_CONFIG_PATH = "configs/dataset/dataset.yaml"

    def __init__(self, tokenizer, max_length=256):
        
        self.max_length = max_length
        self.tokenizer = tokenizer
        self.dataset_config = self.load_dataset_config_dict()

    def load_dataset_config_dict(self):
        dataset_config = OmegaConf.load(get_abs_path(self.DATASET_CONFIG_PATH)).dataset
        return dataset_config

    def process_data(self, data):
        with concurrent.futures.ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()-5) as executor:
            features = list(executor.map(self._process_text, data))	

        all_samples = torch.tensor(features, dtype=torch.long)
        return all_samples
    
    def _process_text(self, text):
        token_ids = self.tokenizer.encode(text, max_length=self.max_length, padding='max_length', truncation=True)
        return token_ids

class CustomDataset(Dataset):

    def __init__(self, input_ids, labels):
        self.input_ids = input_ids
        self.labels = labels

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, idx):
        return {"input_ids": self.input_ids[idx], "labels": self.labels[idx]}

