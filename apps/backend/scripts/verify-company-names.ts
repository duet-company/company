#!/usr/bin/env node

/**
 * Singapore C-Corp Name Verification CLI
 * Executes Phase 1: Company Name Verification
 */

import { NameVerificationService, SG_CORP_NAME_OPTIONS } from '../src/modules/sg-corp/name-verification.service.js';

async function main() {
  console.log('🇸🇬 Singapore C-Corp Name Verification');
  console.log('========================================\n');

  const service = new NameVerificationService();

  // Check top 3 priority names first
  const priorityNames = SG_CORP_NAME_OPTIONS.slice(0, 3);
  console.log(`Checking priority names: ${priorityNames.join(', ')}\n`);

  const results = await service.verifyNames(priorityNames);
  
  // Generate and display report
  const report = service.generateReport(results);
  console.log(report);

  // Save report to file
  const fs = await import('fs');
  const reportPath = '/root/.openclaw/workspace/name-verification-report.md';
  fs.writeFileSync(reportPath, report);
  console.log(`\n✅ Report saved to: ${reportPath}`);

  // Check if we have available names
  const availableNames = results.filter(r => r.available);
  if (availableNames.length > 0) {
    console.log('\n🎉 Next step: Reserve available names with ACRA BizFile+');
    console.log(`   Cost: SGD ${availableNames.length * 15} (SGD 15 per name)`);
    console.log(`   Names: ${availableNames.map(n => n.name).join(', ')}`);
  }

  return results;
}

main().catch(console.error);
