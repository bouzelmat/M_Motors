import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, beforeEach } from 'vitest';
import React from 'react';
import { FinancingSimulator } from '../FinancingSimulator';
import { useSubscriptionTunnelStore } from '../../../application/stores/useSubscriptionTunnelStore';

describe('FinancingSimulator Component', () => {
  beforeEach(() => {
    useSubscriptionTunnelStore.setState({ financingPlan: undefined });
  });

  it('affiche les valeurs par défaut lors de l initialisation sans plan', () => {
    render(<FinancingSimulator vehiclePrice={20000} />);

    // 20000.00 € apparaît deux fois (Prix du véhicule & Capital à financer)
    const vehiclePriceElements = screen.getAllByText('20000.00 €');
    expect(vehiclePriceElements).toHaveLength(2);

    expect(screen.getByText('0.00 €')).toBeInTheDocument();
    expect(screen.getByText('4.50 %')).toBeInTheDocument();

    const state = useSubscriptionTunnelStore.getState().financingPlan;
    expect(state).toBeDefined();
    expect(state?.down_payment).toBe(0);
    expect(state?.duration_months).toBe(48);
  });

  it('initialise le composant depuis un financingPlan existant dans le store', () => {
    useSubscriptionTunnelStore.setState({
      financingPlan: {
        down_payment: 5000,
        duration_months: 36,
        monthly_payment: 450,
      },
    });

    render(<FinancingSimulator vehiclePrice={20000} />);

    expect(screen.getByText('5000.00 €')).toBeInTheDocument();
    expect(screen.getByText('15000.00 €')).toBeInTheDocument();

    const input = screen.getByRole('spinbutton', { name: /Apport initial/i }) as HTMLInputElement;
    expect(input.value).toBe('5000');
  });

  it('met à jour l apport et recalcul la mensualité via l input numérique', () => {
    render(<FinancingSimulator vehiclePrice={20000} />);

    const input = screen.getByRole('spinbutton', { name: /Apport initial/i });
    fireEvent.change(input, { target: { value: '2000' } });

    expect(screen.getByText('2000.00 €')).toBeInTheDocument();
    expect(screen.getByText('18000.00 €')).toBeInTheDocument();

    const state = useSubscriptionTunnelStore.getState().financingPlan;
    expect(state?.down_payment).toBe(2000);
  });

  it('borne l apport entre 0 et vehiclePrice', () => {
    render(<FinancingSimulator vehiclePrice={20000} />);

    const input = screen.getByRole('spinbutton', { name: /Apport initial/i });

    fireEvent.change(input, { target: { value: '25000' } });
    expect(useSubscriptionTunnelStore.getState().financingPlan?.down_payment).toBe(20000);

    fireEvent.change(input, { target: { value: '-5000' } });
    expect(useSubscriptionTunnelStore.getState().financingPlan?.down_payment).toBe(0);
  });

  it('gère une saisie invalide sans enregistrer NaN dans le store', () => {
    render(<FinancingSimulator vehiclePrice={20000} />);

    const input = screen.getByRole('spinbutton', { name: /Apport initial/i });
    fireEvent.change(input, { target: { value: '' } });

    const state = useSubscriptionTunnelStore.getState().financingPlan;
    expect(state?.down_payment).toBe(0);
    expect(isNaN(state?.monthly_payment ?? NaN)).toBe(false);
  });

  it('affiche 0.00 € de capital et de mensualité si apport >= vehiclePrice', () => {
    render(<FinancingSimulator vehiclePrice={20000} />);

    const input = screen.getByRole('spinbutton', { name: /Apport initial/i });
    fireEvent.change(input, { target: { value: '20000' } });

    const state = useSubscriptionTunnelStore.getState().financingPlan;
    expect(state?.monthly_payment).toBe(0);
    expect(screen.getAllByText('0.00 €').length).toBeGreaterThanOrEqual(2);
  });

  it('prend en compte un taux annuel personnalisé', () => {
    render(<FinancingSimulator vehiclePrice={20000} annualInterestRate={0.06} />);

    expect(screen.getByText('6.00 %')).toBeInTheDocument();
  });
});