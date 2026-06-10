import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, StratifiedKFold, train_test_split, StratifiedShuffleSplit
from sklearn.preprocessing import StandardScaler
import scipy.io
import glob
 
class prepare_methane_with_splits:
    def __init__(self, random_state=0, path: str = 'data/', fold_id_max=5):
        self.path = path 
        self.fold_id_max = fold_id_max

        self.X_all = []
        self.Y_all = []
        self.random_state = random_state

        df_0 = pd.read_csv(path+'20250217_spectralCurveBackgroundMedian.csv')
        df_1 = pd.read_csv(path+'20250217_spectralCurveMethaneMedian.csv')
        df = pd.concat([df_0, df_1], axis=0)

        for fold_id in range(1, self.fold_id_max + 1):
            fold_df = df[df['Fold'] == fold_id]
            band_cols = [f'Band{i}' for i in range(7, 433)]
            X = fold_df[band_cols].to_numpy()
            # Use PixelLabel as the label (change to ImageLabel if needed)
            Y = fold_df['PixelLabel'].to_numpy()
            self.X_all.append(X)
            self.Y_all.append(Y)

    def prepare_folds(self):
        self.folds = []
        for fold_id in range(self.fold_id_max):
            X_train = np.concatenate([self.X_all[fold_id%self.fold_id_max], self.X_all[(fold_id+1)%self.fold_id_max]], axis=0)
            Y_train = np.concatenate([self.Y_all[fold_id%self.fold_id_max], self.Y_all[(fold_id+1)%self.fold_id_max]], axis=0)
            X_val = self.X_all[(fold_id+2)%self.fold_id_max]
            Y_val = self.Y_all[(fold_id+2)%self.fold_id_max]
            X_test = np.concatenate([self.X_all[(fold_id+3)%self.fold_id_max], self.X_all[(fold_id+4)%self.fold_id_max]], axis=0)
            Y_test = np.concatenate([self.Y_all[(fold_id+3)%self.fold_id_max], self.Y_all[(fold_id+4)%self.fold_id_max]], axis=0)
            
            # Append the fold
            self.folds.append({
                "X_train": X_train, "Y_train": Y_train,
                "X_val": X_val, "Y_val": Y_val,
                "X_test": X_test, "Y_test": Y_test
            })

    def order_columns_by_variance(self):
            """Orders the columns of X in descending order of variance."""
            ordered_folds = []
            for fold in self.folds:
                X_train = fold['X_train']
                X_test = fold['X_test']
                X_val = fold['X_val']
                Y_val = fold['Y_val']
                Y_train = fold['Y_train']
                Y_test = fold['Y_test']
                variances = np.var(np.concatenate([X_train,X_val], axis=0), axis=0)  # Compute variance of each column
                sorted_indices = np.argsort(variances)[::-1]  # Sort indices in descending order
                X_train = X_train[:, sorted_indices]  # Reorder columns
                X_val = X_val[:, sorted_indices]  # Reorder columns
                X_test = X_test[:, sorted_indices]  # Reorder columns
                ordered_folds.append({
                "X_train": X_train, "Y_train": Y_train,
                "X_val": X_val, "Y_val": Y_val,
                "X_test": X_test, "Y_test": Y_test,
                })
            self.folds = ordered_folds
                
    def standardize(self):
        standardized_folds = []
        for fold in self.folds:
            scaler = StandardScaler()
            X_train = fold['X_train']
            Y_train = fold['Y_train']
            X_val = fold['X_val']
            Y_val = fold['Y_val']
            X_test = fold['X_test']
            Y_test = fold['Y_test']

            X_train = scaler.fit_transform(X_train)  # Fit on train, transform train
            X_val = scaler.transform(X_val)  # Transform validation using the same scaler
            X_test = scaler.transform(X_test)  # Transform test using the same scaler
            standardized_folds.append({
                "X_train": X_train, "Y_train": Y_train,
                "X_val": X_val, "Y_val": Y_val,
                "X_test": X_test, "Y_test": Y_test,
            })
        self.folds = standardized_folds
         
    def prepare_dataset(self, order=True, standardize=True):
        self.prepare_folds()
        if(order): self.order_columns_by_variance()
        if(standardize): self.standardize()

    def get_dataset(self):
        return(self.folds)