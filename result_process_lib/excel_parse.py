import os
import pandas as pd

from .dir_helper import get_dirs


def extract_dataset_number(dataset_name):
    """Extract the dataset number from the dataset folder name.
    
    Args:
        dataset_name (str): The name of the dataset folder (e.g., 'COMMON-6-TG3K' or 'COMMON-6_TG3K')
    
    Returns:
        int: The extracted number from the dataset name
    """
    
    try:
        parts = dataset_name.split('-')
        if len(parts) < 2:
            raise ValueError(f"Invalid dataset name format (no number found after '-'): {dataset_name}")
        number = parts[1]
        if number.isdigit():
            return int(number)
        else:
            return int(number.split('_')[0])
    except Exception as e:
        print(f"Error processing dataset name '{dataset_name}': {str(e)}")
        raise


class ExcelParse:
    def __init__(self, source_path, model, dataset):
        self.source_path = source_path
        self.model = model
        self.dataset = dataset
        self.data = None
        self.read()

    def read(self):
        df = pd.read_csv(self.source_path)
        self.data = df.iloc[-1]

    def parse(self):
        # {
        #     "test/BinaryF1Score": "F1_score",
        #     "test/BinaryAccuracy": "Accuracy",
        #     "test/BinarySpecificity": "Specificity",
        #     "test/BinaryRecall": "Sensitivity",
        #     "test/Dice": "DSC",
        #     "test/BinaryPrecision": "Precision",
        #     "test/BinaryJaccardIndex": "Miou"
        # }

        return {
            'model': self.model, 'dataset': self.dataset,
            'Miou': self.data['test/MeanIoU'] * 100, 'F1_score': self.data['test/BinaryF1Score'] * 100,
            'Accuracy': self.data['test/BinaryAccuracy'] * 100, 'Specificity': self.data['test/BinarySpecificity'] * 100,
            'Sensitivity': self.data['test/BinaryRecall'] * 100, 'DSC': self.data['test/Dice'] * 100,
            'Precision': self.data['test/BinaryPrecision'] * 100,
            'Parameters（M）': self.data['Parameters'] / 1e6, 'FLOPS（G）': self.data['FLOPs'] / 1e9
        }


def parse_result(result_dir, final_result_dir):
    data_list = []
    for model in get_dirs(result_dir):
        model_result_dir = os.path.join(result_dir, model)
        for dataset in sorted(get_dirs(model_result_dir), key=extract_dataset_number):
            dataset_result_csv = os.path.join(model_result_dir, dataset, 'result', 'metrics.csv')
            excel_parse = ExcelParse(dataset_result_csv, model, dataset)
            data_list.append(excel_parse.parse())
        data_list.append({})
    write_result(data_list, final_result_dir)
    return data_list


def write_result(data_list, final_result_dir):
    df = pd.DataFrame(data_list)
    df.to_csv(os.path.join(final_result_dir, 'final_result.csv'), index=False)
    print("Parse Result Done! File Path: ", os.path.join(final_result_dir, 'final_result.csv'))
