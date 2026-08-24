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

    await expect(locationToggle).toHaveAttribute('aria-pressed', 'true');
    await expect(saleToggle).toHaveAttribute('aria-pressed', 'false');
  });

  test('affiche les véhicules du catalogue', async ({ page }) => {
    const locationToggle = page.getByRole('button', {
      name: 'Location (LLD)',
    });

    await expect(locationToggle).toHaveAttribute('aria-pressed', 'true');

    await expect(page.getByText('Peugeot 208')).toBeVisible();
    await expect(page.getByText('Renault Clio')).toBeVisible();
    await expect(page.getByText('Tesla Model 3')).toBeVisible();
  });
});