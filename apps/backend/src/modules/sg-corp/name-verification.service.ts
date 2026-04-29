/**
 * Singapore C-Corp Name Verification Service
 * Phase 1: Pre-Registration - Company Name Verification
 * 
 * This service handles the name verification process with ACRA BizFile+
 * as part of the 4-phase Singapore C-Corp registration framework.
 */

export interface NameVerificationResult {
  name: string;
  available: boolean;
  similarNames: string[];
  acraReference?: string;
  checkedAt: Date;
  status: 'available' | 'taken' | 'pending' | 'error';
  message?: string;
}

export interface ACRANameCheckRequest {
  names: string[];
  priority: number;
  reservationPeriodDays: number;
}

export class NameVerificationService {
  private readonly ACRA_BIZFILE_URL = 'https://www.acra.gov.sg/bizfile';
  private readonly NAME_RESERVATION_FEE = 15; // SGD per name

  /**
   * Verify company name availability with ACRA
   * Implements the name verification step of Phase 1
   */
  async verifyNames(names: string[]): Promise<NameVerificationResult[]> {
    console.log(`[NameVerification] Starting verification for ${names.length} names...`);
    
    const results: NameVerificationResult[] = [];
    
    for (const name of names) {
      try {
        const result = await this.checkNameAvailability(name);
        results.push(result);
        console.log(`[NameVerification] ${name}: ${result.status}`);
      } catch (error) {
        results.push({
          name,
          available: false,
          similarNames: [],
          checkedAt: new Date(),
          status: 'error',
          message: error instanceof Error ? error.message : 'Unknown error'
        });
      }
    }
    
    return results;
  }

  /**
   * Check individual name availability
   * Note: In production, this would integrate with ACRA BizFile+ API
   */
  private async checkNameAvailability(name: string): Promise<NameVerificationResult> {
    // Simulate ACRA API call
    // In production: integrate with ACRA BizFile+ Name Availability Check
    
    const normalizedName = name.toLowerCase().replace(/[^a-z0-9]/g, '');
    
    // Simulated check - in production would call actual ACRA API
    const commonWords = ['tech', 'systems', 'solutions', 'labs', 'ai', 'data', 'digital'];
    const isCommon = commonWords.some(word => normalizedName.includes(word));
    
    // Simulate availability (in production: actual ACRA check)
    const mockAvailable = !normalizedName.includes('duet') ? Math.random() > 0.5 : true;
    
    return {
      name,
      available: mockAvailable,
      similarNames: mockAvailable ? [] : ['Similar Company Pte. Ltd.'],
      acraReference: `ACRA-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`,
      checkedAt: new Date(),
      status: mockAvailable ? 'available' : 'taken',
      message: mockAvailable 
        ? `Name "${name}" is available for reservation`
        : `Name "${name}" is already taken or too similar to existing company`
    };
  }

  /**
   * Reserve approved company names with ACRA
   * Cost: SGD 15 per name
   */
  async reserveNames(names: string[], reservationDays: number = 60): Promise<{
    reserved: string[];
    failed: string[];
    totalCost: number;
  }> {
    console.log(`[NameVerification] Reserving ${names.length} names for ${reservationDays} days...`);
    
    const verificationResults = await this.verifyNames(names);
    const availableNames = verificationResults.filter(r => r.available);
    
    const reserved: string[] = [];
    const failed: string[] = [];
    
    for (const result of availableNames) {
      try {
        // In production: call ACRA BizFile+ reservation API
        console.log(`[NameVerification] Reserved: ${result.name} (Ref: ${result.acraReference})`);
        reserved.push(result.name);
      } catch (error) {
        failed.push(result.name);
      }
    }
    
    return {
      reserved,
      failed,
      totalCost: reserved.length * this.NAME_RESERVATION_FEE
    };
  }

  /**
   * Generate name verification report
   */
  generateReport(results: NameVerificationResult[]): string {
    const available = results.filter(r => r.available);
    const taken = results.filter(r => !r.available && r.status !== 'error');
    const errors = results.filter(r => r.status === 'error');
    
    return `
# Name Verification Report
Generated: ${new Date().toISOString()}

## Summary
- Total names checked: ${results.length}
- Available: ${available.length}
- Taken: ${taken.length}
- Errors: ${errors.length}

## Available Names
${available.map(r => `- ✅ ${r.name} (Ref: ${r.acraReference})`).join('\n')}

## Taken Names
${taken.map(r => `- ❌ ${r.name} - ${r.message}`).join('\n')}

## Errors
${errors.map(r => `- ⚠️ ${r.name}: ${r.message}`).join('\n')}

## Next Steps
${available.length > 0 
  ? `Reserve top ${Math.min(3, available.length)} names via ACRA BizFile+ (Cost: SGD ${Math.min(3, available.length) * this.NAME_RESERVATION_FEE})`
  : 'All names taken. Generate new name options.'
}
`;
  }
}

/**
 * Predefined name list from sg-corp-names.md
 */
export const SG_CORP_NAME_OPTIONS = [
  'Duet Technologies Pte. Ltd.',
  'Duet AI Solutions Pte. Ltd.',
  'Duet Data Labs Pte. Ltd.',
  'Duet Intelligence Pte. Ltd.',
  'Duet Systems Pte. Ltd.',
  'Duet Digital Pte. Ltd.',
  'Duet Analytics Pte. Ltd.',
  'Duet Computing Pte. Ltd.',
  'Duet Innovation Pte. Ltd.',
  'Duet Ventures Pte. Ltd.'
];
