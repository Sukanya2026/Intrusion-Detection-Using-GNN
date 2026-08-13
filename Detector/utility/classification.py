import json
import os
import torch
import torch.nn.functional as F
from torch.nn import Linear
from torch_geometric.nn import GCNConv, GATConv, SAGEConv, GINConv
from torch_geometric.data import Data
from sklearn.preprocessing import StandardScaler, LabelEncoder # Import LabelEncoder here
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split

from Dynamic_Graph_Based_Network_Intrusion import settings


def load_and_preprocess_nslkdd():
    data = pd.read_csv(os.path.join(settings.MEDIA_ROOT, 'KDDTrain+_20Percent.txt'), header=None)    
    labels = data.iloc[:, -1].copy()
    data.drop(columns=[1, 2, 3], inplace=True)  # remove protocol, service, flag
    data.drop(columns=data.columns[-1], inplace=True)  # remove label
    print(data.head)
    labels = labels.apply(lambda x: 0 if x == 'normal' else 1)
    
    
    for column in data.columns:
        if data[column].dtype == 'object': 
            le = LabelEncoder()
            data[column] = le.fit_transform(data[column]) # Transform string values to numeric labels

    features = StandardScaler().fit_transform(data.values)
    # ---Changes end here---

    G = nx.random_geometric_graph(len(features), radius=0.05)
    edge_index = torch.tensor(list(G.edges), dtype=torch.long).t().contiguous()

    x = torch.tensor(features, dtype=torch.float)
    y = torch.tensor(labels.values, dtype=torch.long)

    data = Data(x=x, edge_index=edge_index, y=y)

    snapshots = []
    for i in range(0, len(features), 1000):
        # Create a subgraph for the current snapshot
        G = nx.random_geometric_graph(len(features[i:i+1000]), radius=0.05)  
        edge_index = torch.tensor(list(G.edges), dtype=torch.long).t().contiguous()

        # Create the snapshot using the subgraph's edge_index
        snapshot = Data(
            x=torch.tensor(features[i:i+1000], dtype=torch.float),
            edge_index=edge_index,
            y=torch.tensor(labels.values[i:i+1000], dtype=torch.long)
        )
        snapshots.append(snapshot)
    print(snapshots,data)
    return snapshots, data

# -------------------------------------------
# Define GNN Models
# -------------------------------------------
class GCN(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super().__init__()
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, out_channels)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        x = F.relu(self.conv1(x, edge_index))
        return self.conv2(x, edge_index)

class GAT(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super().__init__()
        self.conv1 = GATConv(in_channels, hidden_channels)
        self.conv2 = GATConv(hidden_channels, out_channels)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        x = F.elu(self.conv1(x, edge_index))
        return self.conv2(x, edge_index)

class GraphSAGE(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super().__init__()
        self.conv1 = SAGEConv(in_channels, hidden_channels)
        self.conv2 = SAGEConv(hidden_channels, out_channels)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        x = F.relu(self.conv1(x, edge_index))
        return self.conv2(x, edge_index)

class GIN(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super().__init__()
        nn1 = torch.nn.Sequential(Linear(in_channels, hidden_channels), torch.nn.ReLU(), Linear(hidden_channels, hidden_channels))
        self.conv1 = GINConv(nn1)
        nn2 = torch.nn.Sequential(Linear(hidden_channels, hidden_channels), torch.nn.ReLU(), Linear(hidden_channels, out_channels))
        self.conv2 = GINConv(nn2)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        x = F.relu(self.conv1(x, edge_index))
        return self.conv2(x, edge_index)

# -------------------------------------------
# Models dictionary
# -------------------------------------------
models = {
    "GCN": GCN,
    "GAT": GAT,
    "GraphSAGE": GraphSAGE,
    "GIN": GIN
}


# -------------------------------------------
# Training Function
# -------------------------------------------
def train_model(model, snapshots, epochs=20, lr=0.01):
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    model.train()
    accuracy_list = []

    for epoch in range(epochs):
        total_loss = 0
        for snapshot in snapshots:
            optimizer.zero_grad()
            out = model(snapshot)
            loss = F.cross_entropy(out, snapshot.y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        acc, _, _, _ = evaluate_model(model, snapshots)
        accuracy_list.append(acc)
        print(f"Epoch {epoch+1}, Loss: {total_loss:.4f}, Accuracy: {acc:.4f}")

    return model, accuracy_list


# -------------------------------------------
# Evaluation Function
# -------------------------------------------
def evaluate_model(model, snapshots):
    model.eval()
    y_true, y_pred = [], []

    for snapshot in snapshots:
        out = model(snapshot)
        pred = out.argmax(dim=1)
        y_true.extend(snapshot.y.tolist())
        y_pred.extend(pred.tolist())

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    return accuracy, precision, recall, f1


# -------------------------------------------
# Visualization Function
# -------------------------------------------
def generate_visualizations(snapshots, data, model_accuracies):
    plt.figure(figsize=(10, 5))
    for model, acc in model_accuracies.items():
        plt.plot(acc, label=model)
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.title("Model Accuracy over Epochs")
    plt.legend()
    plt.grid(True)
    plt.show()

    G = nx.random_geometric_graph(100, radius=0.2)
    nx.draw(G, node_size=20)
    plt.title("Sample Network Traffic Graph")
    plt.show()


# -------------------------------------------
# Training and Evaluation Pipeline
def train_and_evaluate():
    snapshots, data = load_and_preprocess_nslkdd()
    model_accuracies = {}
    results = {}

    for name, model_class in models.items():
        print(f"\n--- Training model: {name} ---")
        model = model_class(in_channels=data.num_features, hidden_channels=32, out_channels=2)
        trained_model, acc_list = train_model(model, snapshots)

        # 🔐 Save the trained model
        torch.save(trained_model.state_dict(), f"{name}_model.pth")

        acc, prec, rec, f1 = evaluate_model(trained_model, snapshots)
        model_accuracies[name] = acc_list
        results[name] = {
            "Accuracy": acc,
            "Precision": prec,
            "Recall": rec,
            "F1-Score": f1
        }
        print(f"✅ {name} - Acc: {acc:.4f}, Prec: {prec:.4f}, Recall: {rec:.4f}, F1: {f1:.4f}")

    generate_visualizations(snapshots, data, model_accuracies)
    return results




