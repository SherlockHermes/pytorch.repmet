from __future__ import print_function

from PIL import Image
from os.path import join
import os
import scipy.io

import configs

import torch.utils.data as data
from torchvision.datasets.utils import download_url, list_dir, list_files


class VOC(data.Dataset):
    """`Pascal Voc <http://host.robots.ox.ac.uk/pascal/VOC/voc2012/>`_ Dataset.
    Args:
        root (string): Root directory of dataset
        cropped (bool, optional): If true, the images will be cropped into the bounding box specified
            in the annotations
        transform (callable, optional): A function/transform that  takes in an PIL image
            and returns a transformed version. E.g, ``transforms.RandomCrop``
        target_transform (callable, optional): A function/transform that takes in the
            target and transforms it.
        download (bool, optional): If true, downloads the dataset tar files from the internet and
            puts it in root directory. If the tar files are already downloaded, they are not
            downloaded again.
    """
    folder = 'PascalVOC'
    download_url_prefix = 'http://host.robots.ox.ac.uk/pascal/VOC/voc2012/'

    def __init__(self,
                 root,
                 train=True,
                 cropped=False,
                 transform=None,
                 target_transform=None,
                 download=False):

        self.root = join(os.path.expanduser(root), self.folder)
        self.train = train
        self.cropped = cropped
        self.transform = transform
        self.target_transform = target_transform

        self.images_folder = join(self.root, 'VOCdevkit', 'VOC2012', 'JPEGImages')
        self.annotations_folder = join(self.root, 'VOCdevkit', 'VOC2012', 'Annotation')

        if download:
            self.download()

        # split = self.load_split()
        #
        # self._breeds = list_dir(self.images_folder)
        #
        # if self.cropped:
        #     self._breed_annotations = [[(annotation, box, idx)
        #                                 for box in self.get_boxes(join(self.annotations_folder, annotation))]
        #                                 for annotation, idx in split]
        #     self._flat_breed_annotations = sum(self._breed_annotations, [])
        #
        #     self._flat_breed_images = [(annotation+'.jpg', idx) for annotation, box, idx in self._flat_breed_annotations]
        # else:
        #     self._breed_images = [(annotation+'.jpg', idx) for annotation, idx in split]
        #
        #     self._flat_breed_images = self._breed_images

    def __len__(self):
        return len(self._flat_breed_images)

    def __getitem__(self, index):
        """
        Args:
            index (int): Index
        Returns:
            tuple: (image, target) where target is index of the target character class.
        """
        image_name, target_class = self._flat_breed_images[index]
        image_path = join(self.images_folder, image_name)
        image = Image.open(image_path).convert('RGB')

        if self.cropped:
            image = image.crop(self._flat_breed_annotations[index][1])

        if self.transform:
            image = self.transform(image)

        if self.target_transform:
            target_class = self.target_transform(target_class)

        return image, target_class

    def download(self):
        import tarfile

        # if os.path.exists(join(self.root, 'Images')) and os.path.exists(join(self.root, 'Annotation')):
        #     if len(os.listdir(join(self.root, 'Images'))) == len(os.listdir(join(self.root, 'Annotation'))) == 120:
        #         print('Files already downloaded and verified')
        #         return

        for filename in ['VOCtrainval_11-May-2012']:
            tar_filename = filename + '.tar'
            url = self.download_url_prefix + '/' + tar_filename
            download_url(url, self.root, tar_filename, None)
            print('Extracting downloaded file: ' + join(self.root, tar_filename))
            with tarfile.open(join(self.root, tar_filename), 'r') as tar_file:
                tar_file.extractall(self.root)
            os.remove(join(self.root, tar_filename))

    @staticmethod
    def get_boxes(path):
        import xml.etree.ElementTree
        e = xml.etree.ElementTree.parse(path).getroot()
        boxes = []
        for objs in e.iter('object'):
            boxes.append([int(objs.find('bndbox').find('xmin').text),
                          int(objs.find('bndbox').find('ymin').text),
                          int(objs.find('bndbox').find('xmax').text),
                          int(objs.find('bndbox').find('ymax').text)])
        return boxes

    def load_split(self):
        if self.train:
            split = scipy.io.loadmat(join(self.root, 'train_list.mat'))['annotation_list']
            labels = scipy.io.loadmat(join(self.root, 'train_list.mat'))['labels']
        else:
            split = scipy.io.loadmat(join(self.root, 'test_list.mat'))['annotation_list']
            labels = scipy.io.loadmat(join(self.root, 'test_list.mat'))['labels']

        split = [item[0][0] for item in split]
        labels = [item[0]-1 for item in labels]
        return list(zip(split, labels))

    def stats(self):
        counts = {}
        for index in range(len(self._flat_breed_images)):
            image_name, target_class = self._flat_breed_images[index]
            if target_class not in counts.keys():
                counts[target_class] = 1
            else:
                counts[target_class] += 1

        print("%d samples spanning %d classes (avg %f per class)"%(len(self._flat_breed_images), len(counts.keys()), float(len(self._flat_breed_images))/float(len(counts.keys()))))

        return counts

if __name__ == "__main__":
    c = VOC(os.path.join(configs.general.paths.imagesets), download=True)