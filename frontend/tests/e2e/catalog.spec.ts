import { test, expect } from '@playwright/test';

test.describe('Catalogue LLD', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/catalogue');
  });

  test('affiche le mode "Location" par défaut', async ({ page }) => {
    const locationToggle = page.getByRole('button', {
      name: 'Location (LLD)',
    });

    const saleToggle = page.getByRole('button', {
      name: 'Achat',
    });

    await expect(locationToggle).toBeVisible();
    await expect(saleToggle).toBeVisible();

    await expect(locationToggle).toHaveAttribute(
      'aria-pressed',
      'true',
    );

    await expect(saleToggle).toHaveAttribute(
      'aria-pressed',
      'false',
    );
  });

  test('affiche les véhicules du catalogue', async ({ page }) => {
    const locationToggle = page.getByRole('button', {
      name: 'Location (LLD)',
    });

    await expect(locationToggle).toHaveAttribute(
      'aria-pressed',
      'true',
    );

    const peugeotCard = page
      .getByTestId('vehicle-card')
      .filter({ hasText: 'Peugeot 208' });

    const renaultCard = page
      .getByTestId('vehicle-card')
      .filter({ hasText: 'Renault Clio' });

    const teslaCard = page
      .getByTestId('vehicle-card')
      .filter({ hasText: 'Tesla Model 3' });

    await expect(peugeotCard).toBeVisible();
    await expect(renaultCard).toBeVisible();
    await expect(teslaCard).toBeVisible();
  });

  test('affiche les services du véhicule avec leur statut', async ({ page }) => {
    const peugeotCard = page
      .getByTestId('vehicle-card')
      .filter({ hasText: 'Peugeot 208' });

    await expect(peugeotCard).toBeVisible();

    await peugeotCard.click();

    await expect(
      page.getByRole('heading', {
        name: 'Services disponibles',
      }),
    ).toBeVisible();

    // Service inclus : le badge doit être présent.
    const assuranceService = page
      .getByTestId('service-option-row')
      .filter({ hasText: 'Assurance' });

    await expect(assuranceService).toBeVisible();

    await expect(
      assuranceService.getByText('Inclus', {
        exact: true,
      }),
    ).toBeVisible();

    // Service non inclus : le prix mensuel doit être affiché.
    const entretienService = page
      .getByTestId('service-option-row')
      .filter({ hasText: 'Entretien' });

    await expect(entretienService).toBeVisible();

    await expect(
      entretienService.getByText('20.00 €/mois'),
    ).toBeVisible();
  });
});
