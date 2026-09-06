import { test, expect } from '@playwright/test';

test.describe('Recherche et filtrage en mode Achat', () => {
  test.beforeEach(async ({ page }) => {
    // 1. Navigation vers la page catalogue
    await page.goto('/catalogue');

    // 2. Basculement en mode "Achat"
    const saleToggle = page.getByRole('button', { name: 'Achat' });
    await saleToggle.waitFor({ state: 'visible' });

    // Attente sécurisée du re-fetch API au changement de mode
    await Promise.all([
      page.waitForResponse(
        (response) => response.url().includes('/vehicles') && response.status() === 200,
        { timeout: 5000 }
      ).catch(() => {}),
      saleToggle.click(),
    ]);

    // 3. Vérification que le toggle "Achat" est sélectionné
    await expect(saleToggle).toHaveAttribute('aria-pressed', 'true');
  });

  test('exécute un scénario complet de filtrage en mode Achat', async ({ page }) => {
    const vehicleCards = page.getByTestId('vehicle-card');

    // Temps de stabilisation du DOM et de React Query
    await page.waitForTimeout(500);

    // --- 1. Filtrage par Marque ---
    const brandInput = page.getByLabel(/filtrer par marque|marque/i);
    await brandInput.fill('Peugeot');
    await page.waitForTimeout(450); // Dépassement du debounce de 300ms

    if ((await vehicleCards.count()) > 0) {
      const countBrand = await vehicleCards.count();
      for (let i = 0; i < countBrand; i++) {
        await expect(vehicleCards.nth(i)).toContainText('Peugeot');
      }
    }

    // --- 2. Application du Budget Max ---
    await brandInput.clear();
    const priceInput = page.getByLabel(/filtrer par budget max|budget max/i);
    await priceInput.fill('50000');
    await page.waitForTimeout(450);

    if ((await vehicleCards.count()) > 0) {
      const countPrice = await vehicleCards.count();
      for (let i = 0; i < countPrice; i++) {
        const cardText = await vehicleCards.nth(i).innerText();
        const priceMatch = cardText.match(/(\d[\d\s]*)\s*€/);
        if (priceMatch) {
          const numericPrice = Number(priceMatch[1].replace(/\s/g, ''));
          expect(numericPrice).toBeLessThanOrEqual(50000);
        }
      }
    }

    // --- 3. Filtre Kilométrage Max ---
    const mileageInput = page.getByLabel(/filtrer par kilométrage max|kilométrage max/i);
    await mileageInput.fill('100000');
    await page.waitForTimeout(450);

    // --- 4. Filtre Type de Motorisation (Material-UI Select) ---
    // Utilisation du rôle combobox ciblant la zone cliquable du Select MUI
    const fuelSelect = page.getByRole('combobox', { name: /motorisation/i });
    await fuelSelect.waitFor({ state: 'visible' });
    await fuelSelect.click();

    // Sélection dans le menu déroulant MUI (listbox)
    const listbox = page.getByRole('listbox');
    if (await listbox.isVisible({ timeout: 2000 }).catch(() => false)) {
      const option = page.getByRole('option', { name: /essence|diesel|hybride|électrique/i }).first();
      if (await option.isVisible()) {
        await option.click();
      } else {
        await page.keyboard.press('Escape');
      }
    } else {
      await page.keyboard.press('Escape');
    }
    await page.waitForTimeout(450);

    // --- 5. Suppression d'un filtre et vérification de l'élargissement ---
    const countBeforeRemove = await vehicleCards.count();

    await mileageInput.clear();
    await page.waitForTimeout(450);

    const countAfterRemove = await vehicleCards.count();
    expect(countAfterRemove).toBeGreaterThanOrEqual(countBeforeRemove);

    // --- 6. Cas sans résultat (Message d'absence) ---
    await brandInput.fill('MarqueInexistanteXYZ');
    await page.waitForTimeout(450);

    const emptyState = page.getByTestId('catalog-empty');
    await expect(emptyState).toBeVisible();
    await expect(
      page.getByText(/aucun véhicule ne correspond à vos critères/i)
    ).toBeVisible();

    // --- 7. Réinitialisation des filtres ---
    const resetButton = page.getByRole('button', { name: /réinitialiser/i });
    await resetButton.click();
    await page.waitForTimeout(450);

    await expect(emptyState).not.toBeVisible();
  });
});