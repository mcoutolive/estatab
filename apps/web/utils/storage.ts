/**
 * localStorage utilities for persisting experiment data
 */

import { ExperimentConfig, Variante, AnalyzeResponse } from './types';

const STORAGE_KEYS = {
    CONFIG: 'estatab_experiment_config',
    VARIANTES: 'estatab_variantes',
    RESULTS: 'estatab_results',
};

export const storage = {
    // Save experiment configuration
    saveConfig(config: ExperimentConfig): void {
        if (typeof window !== 'undefined') {
            localStorage.setItem(STORAGE_KEYS.CONFIG, JSON.stringify(config));
        }
    },

    // Load experiment configuration
    loadConfig(): ExperimentConfig | null {
        if (typeof window !== 'undefined') {
            const data = localStorage.getItem(STORAGE_KEYS.CONFIG);
            return data ? JSON.parse(data) : null;
        }
        return null;
    },

    // Save variants
    saveVariantes(variantes: Variante[]): void {
        if (typeof window !== 'undefined') {
            localStorage.setItem(STORAGE_KEYS.VARIANTES, JSON.stringify(variantes));
        }
    },

    // Load variants
    loadVariantes(): Variante[] | null {
        if (typeof window !== 'undefined') {
            const data = localStorage.getItem(STORAGE_KEYS.VARIANTES);
            return data ? JSON.parse(data) : null;
        }
        return null;
    },

    // Save analysis results
    saveResults(results: AnalyzeResponse): void {
        if (typeof window !== 'undefined') {
            localStorage.setItem(STORAGE_KEYS.RESULTS, JSON.stringify(results));
        }
    },

    // Load analysis results
    loadResults(): AnalyzeResponse | null {
        if (typeof window !== 'undefined') {
            const data = localStorage.getItem(STORAGE_KEYS.RESULTS);
            return data ? JSON.parse(data) : null;
        }
        return null;
    },

    // Clear all experiment data
    clearAll(): void {
        if (typeof window !== 'undefined') {
            localStorage.removeItem(STORAGE_KEYS.CONFIG);
            localStorage.removeItem(STORAGE_KEYS.VARIANTES);
            localStorage.removeItem(STORAGE_KEYS.RESULTS);
        }
    },
};
