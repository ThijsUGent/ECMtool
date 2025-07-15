import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.cluster import KMeans

st.title("Hierarchical Clustering - Full Assignment with Threshold and Optional KMeans")

rng = np.random.default_rng(seed=42)
n_points = 200

# Majority: scattered points with small values
n_small = int(n_points * 0.8)
x_small = rng.uniform(-10, 10, n_small)
y_small = rng.uniform(-10, 10, n_small)
value_small = rng.uniform(10, 30, n_small)

# Few clusters with high values
n_clusters_default = 3
points_per_cluster = int((n_points - n_small) / n_clusters_default)

x_high = []
y_high = []
value_high = []

cluster_centers = [(-5, -5), (0, 5), (5, 0)]

for cx, cy in cluster_centers:
    x_high.extend(rng.normal(cx, 0.5, points_per_cluster))
    y_high.extend(rng.normal(cy, 0.5, points_per_cluster))
    value_high.extend(rng.uniform(70, 100, points_per_cluster))

x = np.concatenate([x_small, x_high])
y = np.concatenate([y_small, y_high])
value = np.concatenate([value_small, value_high])

df = pd.DataFrame({"x": x, "y": y, "value": value})

Z = linkage(df[["x", "y"]], method='ward')
node_heights = np.sort(np.unique(Z[:, 2]))

threshold = st.sidebar.slider(
    "Minimum cluster total value threshold",
    min_value=float(df["value"].min()),
    max_value=float(df["value"].sum()),
    value=float(df["value"].median()),
    step=1.0
)

algo = st.sidebar.selectbox(
    "Clustering algorithm",
    [
        "Hierarchical only",
        "Hierarchical + KMeans",
        "KMeans only"
    ],
)


def clusters_for_all_node_heights(Z, df, heights):
    clusters_dict = {}
    for h in heights:
        labels = fcluster(Z, t=h, criterion='distance')
        clusters_dict[f"height_{h:.4f}"] = labels
    return pd.DataFrame(clusters_dict, index=df.index)


df_all_levels = clusters_for_all_node_heights(Z, df, node_heights)


def assign_clusters_hierarchical(df_all_levels, df_points, threshold):
    height_cols = sorted([c for c in df_all_levels.columns if c.startswith("height_")],
                         key=lambda x: float(x.split("_")[1]))
    assigned = pd.Series(-1, index=df_points.index, name="cluster")
    assigned_points = set()
    cluster_id_counter = 0
    point_height = pd.Series(
        np.nan, index=df_points.index, name="height_assigned")

    for col in height_cols:
        labels = df_all_levels[col]
        unassigned_points = [
            pt for pt in df_points.index if pt not in assigned_points]
        subset_labels = labels.loc[unassigned_points]

        for clust_label in subset_labels.unique():
            cluster_points = subset_labels[subset_labels == clust_label].index
            if len(cluster_points) == 0:
                continue
            val_sum = df_points.loc[cluster_points, "value"].sum()
            if val_sum >= threshold:
                assigned.loc[cluster_points] = cluster_id_counter
                point_height.loc[cluster_points] = float(col.split("_")[1])
                assigned_points.update(cluster_points)
                cluster_id_counter += 1
        if len(assigned_points) == len(df_points):
            break

    if len(assigned_points) < len(df_points):
        unassigned_points = [
            pt for pt in df_points.index if pt not in assigned_points]
        assigned.loc[unassigned_points] = cluster_id_counter
        point_height.loc[unassigned_points] = float(
            height_cols[-1].split("_")[1])

    return assigned, point_height


def assign_clusters_with_kmeans(df_all_levels, df_points, threshold, max_kmeans_clusters=3):
    height_cols = sorted([c for c in df_all_levels.columns if c.startswith("height_")],
                         key=lambda x: float(x.split("_")[1]))
    assigned = pd.Series(-1, index=df_points.index, name="cluster")
    assigned_points = set()
    cluster_id_counter = 0
    point_height = pd.Series(
        np.nan, index=df_points.index, name="height_assigned")

    for col in height_cols:
        labels = df_all_levels[col]
        unassigned_points = [
            pt for pt in df_points.index if pt not in assigned_points]
        subset_labels = labels.loc[unassigned_points]

        for clust_label in subset_labels.unique():
            cluster_points = subset_labels[subset_labels == clust_label].index
            cluster_points = [
                pt for pt in cluster_points if pt not in assigned_points]
            if len(cluster_points) == 0:
                continue

            val_sum = df_points.loc[cluster_points, "value"].sum()

            if val_sum >= threshold:
                if len(cluster_points) > 10 and val_sum > 2 * threshold:
                    coords = df_points.loc[cluster_points, [
                        "x", "y"]].to_numpy()
                    k = min(max_kmeans_clusters, len(cluster_points) // 10)
                    if k > 1:
                        kmeans = KMeans(
                            n_clusters=k, random_state=42, n_init="auto")
                        sub_labels = kmeans.fit_predict(coords)
                        for sub_clust in range(k):
                            sub_points = np.array(cluster_points)[
                                sub_labels == sub_clust]
                            sub_val_sum = df_points.loc[sub_points, "value"].sum(
                            )
                            if sub_val_sum >= threshold:
                                assigned.loc[sub_points] = cluster_id_counter
                                point_height.loc[sub_points] = float(
                                    col.split("_")[1])
                                assigned_points.update(sub_points)
                                cluster_id_counter += 1
                        continue
                assigned.loc[cluster_points] = cluster_id_counter
                point_height.loc[cluster_points] = float(col.split("_")[1])
                assigned_points.update(cluster_points)
                cluster_id_counter += 1
        if len(assigned_points) == len(df_points):
            break

    if len(assigned_points) < len(df_points):
        unassigned_points = [
            pt for pt in df_points.index if pt not in assigned_points]
        assigned.loc[unassigned_points] = cluster_id_counter
        point_height.loc[unassigned_points] = float(
            height_cols[-1].split("_")[1])

    return assigned, point_height


def kmeans(df_points: pd.DataFrame, threshold: float) -> pd.Series:
    """
    Perform KMeans clustering on the points in `df_points`.
    Only keep clusters with total value >= threshold.
    Optionally redistribute points in small clusters to closest large cluster.
    """
    n_clusters = st.sidebar.slider(
        "Number of KMeans clusters",
        min_value=1,
        max_value=10,
        value=3,
        step=1
    )

    redistribute = st.sidebar.radio(
        "Redistribute points from small clusters to closest large cluster?",
        options=["No", "Yes"],
        index=0
    )

    kmeans_model = KMeans(n_clusters=n_clusters,
                          random_state=42, n_init="auto")
    cluster_labels = kmeans_model.fit_predict(df_points[["x", "y"]])
    df_points = df_points.copy()
    df_points["kmeans_label"] = cluster_labels

    # Calculate sum of values per cluster
    cluster_values = df_points.groupby("kmeans_label")["value"].sum()

    # Identify clusters meeting the threshold
    valid_clusters = cluster_values[cluster_values >=
                                    threshold].index.to_list()

    # Assign clusters: keep valid clusters, others get -1 temporarily
    assigned_labels = pd.Series(-1, index=df_points.index, name="cluster")
    for clust in valid_clusters:
        assigned_labels.loc[df_points[df_points["kmeans_label"]
                                      == clust].index] = clust

    if redistribute == "Yes" and len(valid_clusters) > 0:
        # Calculate centroids of valid clusters
        centroids = df_points[df_points["kmeans_label"].isin(valid_clusters)].groupby(
            "kmeans_label")[["x", "y"]].mean()

        # For points in invalid clusters, find closest centroid
        invalid_points_idx = assigned_labels[assigned_labels == -1].index
        invalid_points_coords = df_points.loc[invalid_points_idx, [
            "x", "y"]].to_numpy()

        # Compute distances to centroids
        distances = np.linalg.norm(
            invalid_points_coords[:, np.newaxis, :] - centroids.to_numpy()[np.newaxis, :, :], axis=2
        )

        closest_centroid_idx = distances.argmin(axis=1)
        closest_centroid_labels = centroids.index[closest_centroid_idx]

        # Assign these points to their closest valid cluster
        assigned_labels.loc[invalid_points_idx] = closest_centroid_labels.values

    return assigned_labels

# Run chosen algorithm


if algo == "Hierarchical only":
    assigned_clusters, assigned_heights = assign_clusters_hierarchical(
        df_all_levels, df, threshold)
elif algo == "Hierarchical + KMeans":
    assigned_clusters, assigned_heights = assign_clusters_with_kmeans(
        df_all_levels, df, threshold)
elif algo == "KMeans only":
    assigned_clusters = kmeans(df, threshold)
    assigned_heights = pd.Series(
        np.nan, index=df.index, name="height_assigned")
else:
    st.error("Unknown algorithm selected")
    assigned_clusters = pd.Series(-1, index=df.index, name="cluster")
    assigned_heights = pd.Series(
        np.nan, index=df.index, name="height_assigned")

df_points_clustered = df.copy()
df_points_clustered["cluster"] = assigned_clusters
df_points_clustered["height_assigned"] = assigned_heights

st.markdown(f"### Clusters assigned using {algo}")

fig_dendro = ff.create_dendrogram(
    df[["x", "y"]].to_numpy(), orientation='top', linkagefun=lambda _: Z)
fig_dendro.update_layout(height=400, width=800)
st.plotly_chart(fig_dendro, use_container_width=True)

fig_cluster = px.scatter(
    df_points_clustered,
    x="x",
    y="y",
    color=df_points_clustered["cluster"].astype(str),
    size="value",
    title="Clusters",
    labels={"cluster": "Cluster"},
    height=500
)
st.plotly_chart(fig_cluster, use_container_width=True)

df_clusters_summary = (
    df_points_clustered.groupby("cluster")
    .agg(
        centroid_x=("x", "mean"),
        centroid_y=("y", "mean"),
        total_value=("value", "sum"),
        count_points=("x", "size"),
        avg_height_assigned=("height_assigned", "mean")
    )
    .reset_index()
)

st.subheader("Points with assigned clusters and dendrogram height")
st.dataframe(df_points_clustered)

st.subheader("Clusters summary")
st.dataframe(df_clusters_summary)
