import numpy as np

class KalmanTracker:
    """
    6-state linear Kalman filter: [cx, cy, d, vx, vy, vd]
    cx, cy — centroid in pixels
    d      — depth in metres
    vx, vy, vd — respective velocities
    """
    def __init__(self, process_noise: float, measurement_noise: float):
        self.state = np.zeros(6)
        self.P = np.eye(6) * 500.0

        self.F = np.eye(6)
        self.F[0, 3] = 1.0
        self.F[1, 4] = 1.0
        self.F[2, 5] = 1.0

        self.H = np.zeros((3, 6))
        self.H[0, 0] = 1.0
        self.H[1, 1] = 1.0
        self.H[2, 2] = 1.0

        self.Q = np.eye(6) * process_noise
        self.R = np.eye(3) * measurement_noise
        self.initialized = False

    def init(self, cx: float, cy: float, depth: float):
        self.state = np.array([cx, cy, depth, 0.0, 0.0, 0.0])
        self.P = np.eye(6) * 500.0
        self.initialized = True

    def predict(self):
        self.state = self.F @ self.state
        self.P = self.F @ self.P @ self.F.T + self.Q
        return self.state[:3]

    def update(self, cx: float, cy: float, depth: float):
        z = np.array([cx, cy, depth])
        y = z - self.H @ self.state
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        self.state = self.state + K @ y
        self.P = (np.eye(6) - K @ self.H) @ self.P
        return self.state[:3]
