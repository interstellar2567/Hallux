import { HeroGeometric } from "@/components/ui/shape-landing-hero";
import { FeaturesSection } from "@/components/ui/features-section";
import { CTASection } from "@/components/ui/cta-section";
import { DocumentUpload } from "@/components/ui/document-upload";
import { Footer } from "@/components/ui/footer";

export default function Home() {
  return (
    <main className="min-h-screen pt-20">
      <HeroGeometric
        badge="Synchronize 2027 • Runtime Rebels"
        title1="Stop AI Hallucinations"
        title2="Before They Spread"
      />
      <FeaturesSection />
      <DocumentUpload />
      <CTASection />
      <Footer />
    </main>
  );
}
