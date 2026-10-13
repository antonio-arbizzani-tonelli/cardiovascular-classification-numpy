"""Deterministic regularized logistic regression with NumPy-only L-BFGS.

The design matrix includes a leading column of ones. The optimized objective
is mean binary cross-entropy plus ``l2 * sum(weights[1:] ** 2) / 2``; the
intercept is not penalized. This solver is independent of the historical
assignment implementations and does not select a classification threshold.
"""

from __future__ import annotations

import numpy as np


def sigmoid(scores):
    """Return floating-point sigmoid values without exponential overflow."""
    scores = np.asarray(scores, dtype=np.float64)
    result = np.empty_like(scores)
    positive = scores >= 0.0
    result[positive] = 1.0 / (1.0 + np.exp(-scores[positive]))
    exponential = np.exp(scores[~positive])
    result[~positive] = exponential / (1.0 + exponential)
    return result


def _objective_gradient(design, labels, weights, l2):
    """Evaluate averaged BCE, the penalized objective and its gradient.

    Inputs are already validated by the public solver. Signed logits avoid
    subtracting two large positive values when a positive label is confident.
    Non-finite trial values are returned to the line search for rejection.
    """
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        scores = design @ weights
        if not np.all(np.isfinite(scores)):
            return np.inf, np.inf, np.full(weights.shape, np.inf)
        signed_scores = np.where(labels == 1.0, -scores, scores)
        loss = float(np.mean(np.logaddexp(0.0, signed_scores)))
        penalty = 0.0 if l2 == 0.0 else 0.5 * l2 * float(weights[1:] @ weights[1:])
        objective = loss + penalty
        residual = sigmoid(scores) - labels
        gradient = (design.T @ residual) / labels.size
        gradient[1:] += l2 * weights[1:]
    return loss, float(objective), gradient


def _direction(gradient, history):
    """Apply the L-BFGS two-loop recursion using retained curvature pairs."""
    vector = gradient.copy()
    coefficients = []
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        for step, change, reciprocal in reversed(history):
            coefficient = reciprocal * float(step @ vector)
            coefficients.append(coefficient)
            vector -= coefficient * change
        if history:
            step, change, _ = history[-1]
            squared_change = float(change @ change)
            scale = (float(step @ change) / squared_change
                     if np.isfinite(squared_change) and squared_change > 0.0 else 1.0)
            vector *= scale
        for (step, change, reciprocal), coefficient in zip(history, reversed(coefficients)):
            correction = reciprocal * float(change @ vector)
            vector += step * (coefficient - correction)
    return -vector


def fit_logistic(design, y, l2=1e-4, max_iter=500,
                 gradient_tolerance=1e-6, history_size=10):
    """Fit binary logistic regression with L-BFGS and Armijo backtracking.

    Args:
        design: Nonempty finite dense matrix; its first column must be ones.
            Float64 input is reused without copying the full matrix.
        y: Aligned one-dimensional labels encoded as 0 or 1.
        l2: Nonnegative penalty on weights excluding the intercept.
        max_iter: Maximum number of accepted parameter updates.
        gradient_tolerance: Required infinity norm of the objective gradient.
        history_size: Maximum number of L-BFGS curvature pairs retained.

    Returns:
        A dictionary containing ``weights``, ``status``, unregularized ``loss``,
        ``objective``, ``gradient_inf_norm``, ``iterations``, ``evaluations``
        and ``loss_history``. Status is ``converged``, ``max_iter_reached``,
        ``line_search_failed`` or ``numerical_failure``. Convergence requires
        the gradient criterion; small loss changes alone never qualify.
        Evaluations count objective/gradient calls, including rejected trials.
        History entries describe the initial and every accepted iterate with
        iteration, loss, objective and gradient_inf_norm fields.
    """
    try:
        design = np.asarray(design, dtype=np.float64)
        labels = np.asarray(y, dtype=np.float64)
        l2 = float(l2)
        gradient_tolerance = float(gradient_tolerance)
    except (TypeError, ValueError) as error:
        raise ValueError("Design, labels and numeric settings must be numeric.") from error
    if design.ndim != 2 or min(design.shape) == 0:
        raise ValueError("design must be a nonempty two-dimensional matrix.")
    if labels.shape != (design.shape[0],) or not np.all((labels == 0.0) | (labels == 1.0)):
        raise ValueError("y must be an aligned one-dimensional 0/1 array.")
    # Validate in bounded blocks rather than allocating an N-by-D boolean copy.
    for start in range(0, design.shape[0], 8192):
        if not np.all(np.isfinite(design[start:start + 8192])):
            raise ValueError("design must contain only finite values.")
    if not np.all(design[:, 0] == 1.0):
        raise ValueError("The first design column must contain the intercept ones.")
    if not np.isfinite(l2) or l2 < 0.0:
        raise ValueError("l2 must be finite and nonnegative.")
    if not np.isfinite(gradient_tolerance) or gradient_tolerance <= 0.0:
        raise ValueError("gradient_tolerance must be finite and positive.")
    if type(max_iter) is not int or max_iter < 1:
        raise ValueError("max_iter must be a positive integer.")
    if type(history_size) is not int or history_size < 1:
        raise ValueError("history_size must be a positive integer.")

    weights = np.zeros(design.shape[1], dtype=np.float64)
    prevalence = float(np.clip(np.mean(labels), 1e-12, 1.0 - 1e-12))
    weights[0] = np.log(prevalence / (1.0 - prevalence))
    loss, objective, gradient = _objective_gradient(design, labels, weights, l2)
    evaluations, iterations = 1, 0
    history = []
    loss_history = []
    status = "max_iter_reached"

    while True:
        gradient_norm = float(np.max(np.abs(gradient)))
        loss_history.append({"iteration": iterations, "loss": loss,
                             "objective": objective, "gradient_inf_norm": gradient_norm})
        if not (np.isfinite(loss) and np.isfinite(objective)
                and np.all(np.isfinite(gradient))):
            status = "numerical_failure"
            break
        if gradient_norm <= gradient_tolerance:
            status = "converged"
            break
        if iterations >= max_iter:
            break

        direction = _direction(gradient, history)
        with np.errstate(over="ignore", invalid="ignore"):
            slope = float(gradient @ direction)
        if not np.all(np.isfinite(direction)) or not np.isfinite(slope) or slope >= 0.0:
            # Discard unreliable curvature and use a bounded steepest-descent
            # direction. This also avoids overflow in the descent dot product.
            history.clear()
            direction = -(gradient / gradient_norm) / gradient.size
            slope = float(gradient @ direction)
        if not np.isfinite(slope) or slope >= 0.0:
            status = "numerical_failure"
            break

        step_length = min(1.0, 1.0 / gradient_norm) if iterations == 0 else 1.0
        accepted = False
        for _ in range(60):
            with np.errstate(over="ignore", invalid="ignore"):
                candidate = weights + step_length * direction
            if np.array_equal(candidate, weights):
                break
            trial_loss, trial_objective, trial_gradient = _objective_gradient(
                design, labels, candidate, l2)
            evaluations += 1
            if (np.isfinite(trial_loss) and np.isfinite(trial_objective)
                    and np.all(np.isfinite(trial_gradient))
                    and trial_objective <= objective + 1e-4 * step_length * slope):
                accepted = True
                break
            step_length *= 0.5
        if not accepted:
            status = "line_search_failed"
            break

        step = candidate - weights
        change = trial_gradient - gradient
        with np.errstate(over="ignore", invalid="ignore"):
            curvature = float(step @ change)
            curvature_scale = float(np.linalg.norm(step) * np.linalg.norm(change))
        if (np.isfinite(curvature) and np.isfinite(curvature_scale)
                and curvature > max(np.finfo(np.float64).tiny, 1e-10 * curvature_scale)):
            history.append((step, change, 1.0 / curvature))
            if len(history) > history_size:
                history.pop(0)
        weights = candidate
        loss, objective, gradient = trial_loss, trial_objective, trial_gradient
        iterations += 1

    return {"weights": weights, "status": status, "loss": loss,
            "objective": objective, "gradient_inf_norm": gradient_norm,
            "iterations": iterations, "evaluations": evaluations,
            "loss_history": loss_history}
