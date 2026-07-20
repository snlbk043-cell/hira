import CustomTrackerPageClient from "@/components/CustomTrackerPageClient";

export default async function Page({ params }: { params: Promise<{ key: string }> }) {
  const { key } = await params;
  return <CustomTrackerPageClient trackerKey={key} />;
}
